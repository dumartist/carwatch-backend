import os
import sys
import logging

os.makedirs('logs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('models', exist_ok=True)

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logging.getLogger('ultralytics').setLevel(logging.ERROR)
logging.getLogger('torch').setLevel(logging.ERROR)
logging.getLogger('cv2').setLevel(logging.ERROR)

def check_models():
    missing = [model for model in ['models/best_LPD.pt', 'models/best_OCR.pt'] if not os.path.exists(model)]
    return len(missing) == 0

try:
    from app import create_app
    app = create_app()
except ImportError as e:
    logging.error(f"Failed to import app module: {e}")
    sys.exit(1)

if __name__ == "__main__":
    if not check_models():
        print("WARNING: OCR will not work without model files")
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False, threaded=True)
