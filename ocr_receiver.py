# ocr_receiver.py
import cv2
import numpy as np
import os
from ultralytics import YOLO

# --- Configuration for Models ---
# Path to your trained YOLOv8 License Plate Detection (LPD) model
LPD_MODEL_PATH = r"C:/carwatch-backend/best_LPD.pt"
# Path to your trained YOLOv8 Character Detection (OCR) model
OCR_MODEL_PATH = r"C:/carwatch-backend/best_OCR.pt"

# --- YOLOv8 Model Loading (Load once when this module is imported) ---
# Global variables to hold the loaded models
lpd_model = None
ocr_model = None

def load_yolo_models():
    """Loads YOLOv8 models. This function should be called once."""
    global lpd_model, ocr_model
    if lpd_model is None:
        try:
            lpd_model = YOLO(LPD_MODEL_PATH)
            print(f"YOLOv8 License Plate Detection model loaded successfully from: {LPD_MODEL_PATH}")
        except Exception as e:
            print(f"[ERROR] Could not load YOLOv8 LPD model from {LPD_MODEL_PATH}. Error: {e}")
            # Consider raising an exception or handling this more robustly in a real application
            exit() # Critical error, cannot proceed without model

    if ocr_model is None:
        try:
            ocr_model = YOLO(OCR_MODEL_PATH)
            print(f"YOLOv8 Character Recognition (OCR) model loaded successfully from: {OCR_MODEL_PATH}")
        except Exception as e:
            print(f"[ERROR] Could not load YOLOv8 OCR model from {OCR_MODEL_PATH}. Error: {e}")
            # Consider raising an exception or handling this more robustly
            exit() # Critical error, cannot proceed without model

# Call this function once when the module is imported
load_yolo_models()

# --- Stage 1: License Plate Detection ---
def detect_and_crop_plate(image_np):
    """
    Uses the LPD YOLOv8 model to detect license plates.
    Returns the cropped plate image (highest confidence).
    """
    img = image_np
    if img is None:
        print("[ERROR] No image data for plate detection.")
        return None

    print("\n--- Stage 1: Detecting license plates ---")
    # Use the globally loaded lpd_model
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
        print(f"Detected a plate with confidence: {best_confidence:.2f}")
        return best_plate_crop
    else:
        print("No license plate detected or confidence too low.")
        return None

# --- Stage 2: Character Detection & Recognition (OCR) ---
def recognize_characters_with_yolo(cropped_plate_img):
    """
    Uses the OCR YOLOv8 model to detect and recognize characters on a cropped plate image.
    Sorts characters by position to form the plate number.
    """
    if cropped_plate_img is None:
        print("[ERROR] No cropped plate image provided for character recognition.")
        return ""

    print("\n--- Stage 2: Recognizing characters on the cropped plate ---")
    # Use the globally loaded ocr_model
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
            print(f"Raw OCR String from character detection: {ocr_string}")
        else:
            print("No characters detected on the cropped plate with current confidence threshold.")
    return ocr_string