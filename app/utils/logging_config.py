import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Set up logging directories and handlers."""
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Root logger configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                'logs/app.log', 
                maxBytes=5*1024*1024, 
                backupCount=5
            )
        ]
    )
    
    return logging.getLogger(__name__)
