import logging
import os
import mysql.connector
from PIL import Image
import io
from datetime import datetime

try:
    from ..utils.database import get_db_connection
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from app.utils.database import get_db_connection

logger = logging.getLogger(__name__)

def db_upload_image(image_filename):
    try:
        image_path = os.path.join("uploads", image_filename)
        
        if not os.path.exists(image_path):
            return {'success': False, 'message': 'Image file not found'}

        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
                format_type = 'JPEG'
            else:
                format_type = img.format if img.format else 'PNG'

            img_buffer = io.BytesIO()
            img.save(img_buffer, format=format_type)
            img_data = img_buffer.getvalue()

        file_size = len(img_data)
        file_extension = os.path.splitext(image_filename)[1].lower()

        if file_size > 16 * 1024 * 1024:
            return {'success': False, 'message': 'Image file too large (max 16MB)'}

        try:
            with get_db_connection() as (db, cursor):
                sql_insert = """INSERT INTO images 
                                (filename, image_data, file_size, file_type, upload_date) 
                                VALUES (%s, %s, %s, %s, %s)"""
                values = (image_filename, img_data, file_size, file_extension, datetime.now())
                
                cursor.execute(sql_insert, values)
                db.commit()

                logger.info(f"Uploaded {image_filename} as {format_type} ({file_size} bytes)")
                return {
                    'success': True,
                    'message': f'Image uploaded successfully as {format_type}',
                    'filename': image_filename,
                    'file_size': file_size
                }

        except mysql.connector.Error as db_error:
            logger.error(f"Database error: {db_error}")
            return {'success': False, 'message': f'Database error: {str(db_error)}'}

    except Exception as e:
        logger.error(f"Error uploading {image_filename}: {e}")
        return {'success': False, 'message': f'Upload failed: {str(e)}'}