import os
import sys

# Create required directories
os.makedirs('logs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('models', exist_ok=True)

import logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Suppress external library logs
logging.getLogger('ultralytics').setLevel(logging.ERROR)
logging.getLogger('torch').setLevel(logging.ERROR)
logging.getLogger('cv2').setLevel(logging.ERROR)

def check_models():
    """Check if model files exist."""
    missing = []
    for model in ['models/best_LPD.pt', 'models/best_OCR.pt']:
        if not os.path.exists(model):
            missing.append(model)
    
    if missing:
        logger.warning(f"Missing models: {', '.join(missing)}")
        return False
    return True

# Check models quietly
models_ok = check_models()

# Try new structure, fallback to legacy
try:
    from app import create_app
    app = create_app()
    print("Using new app structure")
except ImportError:
    print("Using legacy structure")
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass

if __name__ == "__main__":
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        real_ip = s.getsockname()[0]
        s.close()
        print(f"Available at: http://{real_ip}:8000")
    except:
        print("Available at: http://localhost:8000")
    
    if not models_ok:
        print("WARNING: OCR will not work without model files")
    
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
