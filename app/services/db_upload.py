import logging
import os
import mysql.connector
from PIL import Image
import io
from datetime import datetime

# Import utilities with proper fallback handling
try:
    from ..utils.database import get_db_connection
except ImportError:
    # Fallback for when running as script or from different context
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    try:
        from app.utils.database import get_db_connection
    except ImportError:
        try:
            from utils.database import get_db_connection
        except ImportError:
            # Final fallback - create a dummy function
            def get_db_connection():
                raise ImportError("Database connection not available")

logger = logging.getLogger(__name__)
    
def db_upload_image(image_filename):
    """
    Upload image from uploads directory to MySQL database as MEDIUMBLOB
    Simple image storage without user associations or status tracking.

    Args:
        image_filename (str): Name of the image file in uploads directory
    
    Returns:
        dict: Result with success status and details
    """
    try:
        uploads_dir = "uploads"
        image_path = os.path.join(uploads_dir, image_filename)
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return {'success': False, 'message': 'Image file not found'}
        
        # Process image with PIL
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
                format_type = 'JPEG'
            else:
                format_type = img.format if img.format else 'PNG'

            # Convert image to bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format=format_type)
            img_data = img_buffer.getvalue()

        # Get file info
        file_size = len(img_data)
        file_extension = os.path.splitext(image_filename)[1].lower()
        
        # Validate file size (max 16MB for MEDIUMBLOB)
        max_size = 16 * 1024 * 1024  # 16MB (MEDIUMBLOB limit)
        if file_size > max_size:
            logger.error(f"Image file too large: {file_size} bytes")
            return {'success': False, 'message': 'Image file too large (max 16MB)'}

        # Save to database using simplified schema without ID
        try:
            with get_db_connection() as (db, cursor):
                try:
                    sql = """INSERT INTO images 
                             (filename, image_data, file_size, file_type, upload_date) 
                             VALUES (%s, %s, %s, %s, %s)"""

                    values = (
                        image_filename,
                        img_data,
                        file_size,
                        file_extension,
                        datetime.now()
                    )
                    
                    cursor.execute(sql, values)
                    db.commit()
                    
                    logger.info(f"Successfully uploaded {image_filename} as {format_type} ({file_size} bytes)")
                    return {
                        'success': True, 
                        'message': f'Image uploaded successfully as {format_type}',
                        'filename': image_filename,
                        'file_size': file_size
                    }
                    
                except mysql.connector.Error as db_error:
                    # If images table doesn't exist, try to create it
                    if "doesn't exist" in str(db_error).lower():
                        logger.warning("Images table doesn't exist, attempting to create it")
                        try:
                            create_images_table(cursor, db)
                            # Retry the insert
                            cursor.execute(sql, values)
                            db.commit()
                            
                            logger.info(f"Successfully uploaded {image_filename} after creating table")
                            return {
                                'success': True, 
                                'message': f'Image uploaded successfully (table created)',
                                'filename': image_filename,
                                'file_size': file_size
                            }
                        except Exception as create_error:
                            logger.error(f"Failed to create images table: {create_error}")
                            return {'success': False, 'message': 'Database table creation failed'}
                    else:
                        logger.error(f"Database error: {db_error}")
                        return {'success': False, 'message': f'Database error: {str(db_error)}'}
        except ImportError as import_error:
            logger.error(f"Database connection import error: {import_error}")
            return {'success': False, 'message': 'Database connection not available'}
        except Exception as conn_error:
            logger.error(f"Database connection error: {conn_error}")
            return {'success': False, 'message': f'Database connection failed: {str(conn_error)}'}
        
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return {'success': False, 'message': f'Upload failed: {str(e)}'}

def create_images_table(cursor, db):
    """Create the simplified images table without primary key."""
    sql = """
    CREATE TABLE images (
        filename VARCHAR(255) NOT NULL,
        image_data MEDIUMBLOB NOT NULL,
        file_size INT NOT NULL,
        file_type VARCHAR(10) NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_filename (filename),
        INDEX idx_upload_date (upload_date)
    )
    """
    cursor.execute(sql)
    db.commit()
    logger.info("Images table created successfully")