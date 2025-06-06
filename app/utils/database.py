import mysql.connector
import logging
from contextlib import contextmanager

# Import config with fallback
try:
    from app.config import Config
except ImportError:
    # Fallback to legacy config
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    import config as Config

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """Context manager for database connections with automatic cleanup."""
    db = None
    cursor = None
    try:
        db = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
        )
        cursor = db.cursor(dictionary=True)
        yield db, cursor
    except Exception as e:
        logger.error(f"Database error: {e}")
        if db:
            db.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def connect_to_db():
    """Legacy function for backward compatibility."""
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None
