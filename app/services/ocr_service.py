# ocr_service.py
import os
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

# --- Model paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LPD_MODEL_PATH = os.path.join(BASE_DIR, "models", "best_LPD.pt")
OCR_MODEL_PATH = os.path.join(BASE_DIR, "models", "best_OCR.pt")

# --- Global model instances ---
lpd_model = None
ocr_model = None

def load_yolo_models():
    """Loads YOLOv8 models. This function should be called once."""
    global lpd_model, ocr_model
    if lpd_model is None:
        try:
            lpd_model = YOLO(LPD_MODEL_PATH)
            logger.info(f"YOLOv8 License Plate Detection model loaded successfully from: {LPD_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Could not load YOLOv8 LPD model from {LPD_MODEL_PATH}. Error: {e}")
            exit() 

    if ocr_model is None:
        try:
            ocr_model = YOLO(OCR_MODEL_PATH)
            logger.info(f"YOLOv8 Character Recognition (OCR) model loaded successfully from: {OCR_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Could not load YOLOv8 OCR model from {OCR_MODEL_PATH}. Error: {e}")
            exit()

# Load models when module is imported
load_yolo_models()

# --- Stage 1: License Plate Detection ---
def detect_and_crop_plate(image_np):
    """
    Uses the LPD YOLOv8 model to detect license plates.
    Returns the cropped plate image (highest confidence).
    """
    img = image_np
    if img is None:
        logger.error("No image data for plate detection.")
        return None

    logger.info("Stage 1: Detecting license plates")
    # Use the LPD model
    results = lpd_model(img, conf=0.5, iou=0.5, verbose=False)

    best_plate_crop = None
    best_confidence = -1

    for r in results:
        if len(r.boxes) > 0:
            for box in r.boxes:
                confidence = box.conf.item()
                if confidence > best_confidence:
                    best_confidence = confidence
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                    padding = 10
                    x1 = max(0, x1 - padding)
                    y1 = max(0, y1 - padding)
                    x2 = min(img.shape[1], x2 + padding)
                    y2 = min(img.shape[0], y2 + padding)

                    best_plate_crop = img[y1:y2, x1:x2]

    if best_plate_crop is not None:
        logger.info(f"Detected a plate with confidence: {best_confidence:.2f}")
        return best_plate_crop
    else:
        logger.info("No license plate detected or confidence too low.")
        return None

# --- Stage 2: Character Detection & Recognition (OCR) ---
def recognize_characters_with_yolo(cropped_plate_img):
    """
    Uses the OCR YOLOv8 model to detect and recognize characters on a cropped plate image.
    Sorts characters by position to form the plate number.
    """
    if cropped_plate_img is None:
        logger.error("No cropped plate image provided for character recognition.")
        return ""

    logger.info("Stage 2: Recognizing characters on the cropped plate")
    # Use the OCR model
    results = ocr_model(cropped_plate_img, conf=0.1, iou=0.3, verbose=False)

    detected_chars_with_coords = []
    ocr_string = ""

    for r in results:
        if len(r.boxes) > 0:
            for box in r.boxes:
                coords = box.xyxy.tolist()[0]
                confidence = box.conf.item()
                class_id = int(box.cls.item())
                class_name = r.names[class_id]

                detected_chars_with_coords.append({
                    'char': class_name,
                    'x_center': (coords[0] + coords[2]) / 2,
                    'confidence': confidence,
                    'box': coords
                })

            detected_chars_with_coords.sort(key=lambda x: x['x_center'])
            ocr_string = "".join([d['char'] for d in detected_chars_with_coords])
            logger.info(f"Raw OCR String from character detection: {ocr_string}")
        else:
            logger.info("No characters detected on the cropped plate with current confidence threshold.")
    return ocr_string