import os
import logging

def setup_logging():
    """Simple logging setup."""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/app.log')
        ]
    )
    
    return logging.getLogger(__name__)

if __name__ == "__main__":
    setup_logging()
    print("Logging setup complete!")
