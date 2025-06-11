import os
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LPD_MODEL_PATH = os.path.join(BASE_DIR, "models", "best_LPD.pt")
OCR_MODEL_PATH = os.path.join(BASE_DIR, "models", "best_OCR.pt")

lpd_model = None
ocr_model = None

def load_yolo_models():
    global lpd_model, ocr_model
    if lpd_model is None:
        try:
            lpd_model = YOLO(LPD_MODEL_PATH)
            logger.info(f"LPD model loaded: {LPD_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to load LPD model: {e}")
            exit()

    if ocr_model is None:
        try:
            ocr_model = YOLO(OCR_MODEL_PATH)
            logger.info(f"OCR model loaded: {OCR_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to load OCR model: {e}")
            exit()

load_yolo_models()

def detect_and_crop_plate(image_np):
    if image_np is None:
        logger.error("No image data for plate detection")
        return None

    results = lpd_model(image_np, conf=0.5, iou=0.5, verbose=False)
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
                    x2 = min(image_np.shape[1], x2 + padding)
                    y2 = min(image_np.shape[0], y2 + padding)
                    
                    best_plate_crop = image_np[y1:y2, x1:x2]

    if best_plate_crop is not None:
        logger.info(f"Plate detected with confidence: {best_confidence:.2f}")
    else:
        logger.info("No license plate detected")
    
    return best_plate_crop

def recognize_characters_with_yolo(cropped_plate_img):
    if cropped_plate_img is None:
        return ""

    results = ocr_model(cropped_plate_img, conf=0.1, iou=0.3, verbose=False)
    detected_chars = []

    for r in results:
        if len(r.boxes) > 0:
            for box in r.boxes:
                coords = box.xyxy.tolist()[0]
                confidence = box.conf.item()
                class_id = int(box.cls.item())
                class_name = r.names[class_id]

                detected_chars.append({
                    'char': class_name,
                    'x_center': (coords[0] + coords[2]) / 2,
                    'confidence': confidence
                })

            detected_chars.sort(key=lambda x: x['x_center'])
            ocr_string = "".join([d['char'] for d in detected_chars])
            logger.info(f"OCR result: {ocr_string}")
            return ocr_string
    
    logger.info("No characters detected")
    return ""