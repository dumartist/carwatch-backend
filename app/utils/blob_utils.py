import mysql.connector
import io
import logging
from PIL import Image
import os

try:
    from .database import get_db_connection
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils import get_db_connection

logger = logging.getLogger(__name__)

def blob_to_jpg(table, id_value, output_path, id_column='id', image_column='image_data'):
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with get_db_connection() as (db, cursor):
            sql = f"SELECT {image_column} FROM {table} WHERE {id_column} = %s"
            cursor.execute(sql, (id_value,))
            result = cursor.fetchone()

            if not result or not result[0]:
                return {
                    'success': False,
                    'message': f'No image data found for {id_column}={id_value}'
                }

            image_data = result[0]
            
            if not isinstance(image_data, bytes):
                return {
                    'success': False,
                    'message': f'Invalid image data type: expected bytes, got {type(image_data).__name__}'
                }

            if len(image_data) == 0:
                return {'success': False, 'message': 'Image data is empty'}

            try:
                image = Image.open(io.BytesIO(image_data))
                
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                image.save(output_path, "JPEG", quality=95)
                file_size = os.path.getsize(output_path)
                
                return {
                    'success': True,
                    'message': f'Image saved to {output_path}',
                    'output_path': output_path,
                    'file_size': file_size,
                    'image_size': image.size,
                    'image_mode': image.mode
                }
                
            except Exception as img_error:
                return {'success': False, 'message': f'Error processing image: {img_error}'}

    except mysql.connector.Error as db_error:
        return {'success': False, 'message': f'Database error: {db_error}'}
    except Exception as e:
        logger.error(f"Error in blob_to_jpg: {e}")
        return {'success': False, 'message': f'Unexpected error: {e}'}

def blob_to_jpg_by_latest(table='images', output_path=None, image_column='image_data', date_column='upload_date', cleanup_old=True):
    try:
        with get_db_connection() as (db, cursor):
            sql = f"SELECT {image_column}, {date_column} FROM {table} ORDER BY {date_column} DESC LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'message': f'No records found in table {table}'}
            
            try:
                if isinstance(result, dict):
                    image_data = result.get(image_column)
                    upload_date = result.get(date_column)
                elif isinstance(result, (tuple, list)) and len(result) >= 2:
                    image_data = result[0]
                    upload_date = result[1]
                else:
                    return {'success': False, 'message': f'Unexpected database result format: {type(result)}'}
                
                if not image_data:
                    return {'success': False, 'message': f'No image data found in latest record'}
                
            except (IndexError, KeyError, TypeError) as e:
                return {'success': False, 'message': f'Error processing database result: {e}'}
            
            if output_path is None:
                timestamp_str = upload_date.strftime("%Y%m%d%H%M%S") if upload_date else "latest"
                output_path = f"images/image_{timestamp_str}.jpg"
            
            if not isinstance(image_data, bytes):
                return {'success': False, 'message': f'Invalid image data type: expected bytes, got {type(image_data).__name__}'}

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Cleanup logic: Remove old images in the directory if requested
            if cleanup_old and output_dir:
                try:
                    for filename in os.listdir(output_dir):
                        if filename.startswith('image_') and filename.endswith('.jpg'):
                            old_file_path = os.path.join(output_dir, filename)
                            if os.path.exists(old_file_path) and old_file_path != output_path:
                                os.remove(old_file_path)
                                logger.info(f"Removed old image: {old_file_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Error during cleanup: {cleanup_error}")
            
            # If the exact file already exists, check if we need to update it
            if os.path.exists(output_path) and cleanup_old:
                try:
                    os.remove(output_path)
                    logger.info(f"Removed existing image: {output_path}")
                except Exception as remove_error:
                    logger.warning(f"Error removing existing file: {remove_error}")

            try:
                image = Image.open(io.BytesIO(image_data))
                
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                image.save(output_path, "JPEG", quality=95)
                file_size = os.path.getsize(output_path)
                
                return {
                    'success': True,
                    'message': f'Latest image saved to {output_path}',
                    'output_path': output_path,
                    'file_size': file_size,
                    'image_size': image.size,
                    'upload_date': upload_date.isoformat() if upload_date else None
                }
                
            except Exception as img_error:
                return {'success': False, 'message': f'Error processing image: {img_error}'}

    except Exception as e:
        logger.error(f"Error in blob_to_jpg_by_latest: {e}")
        return {'success': False, 'message': f'Unexpected error: {e}'}
