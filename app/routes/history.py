from flask import Blueprint, request, jsonify, session, send_from_directory, Response
import bleach
import os
import cv2
import numpy as np
import datetime
import logging
import time
from ..services.db_upload import db_upload_image

try:
    from ..utils.database import get_db_connection
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils import get_db_connection

try:
    from ..services.ocr_service import detect_and_crop_plate, recognize_characters_with_yolo
except ImportError:
    def detect_and_crop_plate(img): return None
    def recognize_characters_with_yolo(img): return "NO_OCR"

logger = logging.getLogger(__name__)
history_bp = Blueprint('history', __name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

IMAGES_FOLDER = 'images'
if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)

@history_bp.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image part in the request'}), 400

    file = request.files['image']
    status = request.args.get('status', 'unknown')

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1]
    filename = f"image_{timestamp}{file_extension}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    image_bytes = file.read()
    with open(filepath, 'wb') as f:
        f.write(image_bytes)

    db_upload_result = db_upload_image(filename)

    try:
        img_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img_np is None:
            raise ValueError("Could not decode image.")
    except Exception as e:
        os.remove(filepath)
        return jsonify({'success': False, 'message': f'Error decoding image: {e}'}), 500

    cropped_plate = detect_and_crop_plate(img_np)
    plate_number = ""
    if cropped_plate is not None:
        plate_number = recognize_characters_with_yolo(cropped_plate)
        logger.info(f"OCR Result: {plate_number}")

    description = "car is available" if status == "entering" else "car is being use"
    subject = "Vehicle Entry" if status == "entering" else ("Vehicle Exit" if status == "leaving" else "Unknown Status")

    try:
        image_id = db_upload_result.get('image_id')  # Boleh None
        with get_db_connection() as (db, cursor):
            if image_id:
                sql = "INSERT INTO history (plate, subject, description, image_id) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (plate_number, subject, description, image_id))
            else:
                sql = "INSERT INTO history (plate, subject, description) VALUES (%s, %s, %s)"
                cursor.execute(sql, (plate_number, subject, description))
            db.commit()
            message = 'Image received, uploaded to database, OCR processed, and data recorded successfully.'
            status_code = 201
    except Exception as e:
        logger.error(f"Database recording error: {e}")
        message = f'Failed to record data to database: {e}'
        status_code = 500
    finally:
        os.remove(filepath)

    response_data = {
        'success': status_code == 201,
        'message': message,
        'plate_number': plate_number,
        'status': status,
        'image_uploaded': db_upload_result['success']
    }

    if db_upload_result['success']:
        response_data['image_filename'] = db_upload_result['filename']
        response_data['image_id'] = db_upload_result.get('image_id')
    else:
        response_data['upload_error'] = db_upload_result['message']

    return jsonify(response_data), status_code

@history_bp.route('/history', methods=['GET'])
def get_all_history():
    try:
        with get_db_connection() as (db, cursor):
            sql = """
                SELECT h.subject, h.plate, h.description, h.date, h.image_id
                FROM history h
                ORDER BY h.date DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            history_list = []
            for row in rows:
                history_list.append({
                    'subject': row['subject'],
                    'plate': row['plate'],
                    'description': row['description'],
                    'date': row['date'],
                    'image_id': row.get('image_id')
                })
            return jsonify({'success': True, 'message': 'History retrieved', 'data': history_list}), 200
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'success': False, 'message': 'Error fetching history'}), 500

@history_bp.route('/get_image/<int:image_id>', methods=['GET'])
def serve_image_by_id(image_id):
    logger.info(f"Image request received for ID: {image_id}")
    try:
        with get_db_connection() as (db, cursor):
            cursor.execute("SELECT image_data, file_type FROM images WHERE image_id = %s", (image_id,))
            result = cursor.fetchone()
            if result:
                logger.info(f"Fetched image data for ID {image_id}: keys={list(result.keys())}")
            else:
                logger.warning(f"No image found in DB for ID {image_id}")


            if not result:
                logger.warning(f"No result found for image_id={image_id}")
                return jsonify({'success': False, 'message': 'Image not found'}), 404

            image_data = result['image_data']
            file_type = result['file_type']

            if not image_data:
                logger.warning(f"Empty image_data for image_id={image_id}")
                return jsonify({'success': False, 'message': 'Image data missing'}), 404

            return Response(
                image_data,
                mimetype=file_type or 'image/jpeg',
                headers={
                    'Cache-Control': 'no-cache',
                    'Content-Length': str(len(image_data))
                }
            )
    except Exception as e:
        logger.error(f"Error serving image by ID: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@history_bp.route('/fetch_img', methods=['GET'])
def fetch_image():
    try:
        logger.info("Starting fetch_image request")
        with get_db_connection() as (db, cursor):
            logger.info("Database connection established")
            sql = "SELECT image_data, upload_date, file_type FROM images ORDER BY upload_date DESC LIMIT 1"
            cursor.execute(sql)
            logger.info("SQL query executed")
            result = cursor.fetchone()
            logger.info(f"Query result type: {type(result)}")
            
            if not result:
                logger.warning("No images found in database")
                return jsonify({'success': False, 'message': 'No images found in database'}), 404
            
            logger.info(f"Result keys: {list(result.keys())}")
            image_data = result['image_data']  # Access as dictionary key, not index
            logger.info(f"Image data type: {type(image_data)}, length: {len(image_data) if image_data else 'None'}")
            
            file_type = result.get('file_type', 'image/jpeg')  # Get file_type with default
            logger.info(f"File type: {file_type}")
            
            if not image_data:
                logger.warning("Image data is empty")
                return jsonify({'success': False, 'message': 'Image data is empty'}), 404
            
            logger.info("Creating response")
            response = Response(
                image_data,
                mimetype=file_type,
                headers={
                    'Content-Type': file_type,
                    'Content-Length': str(len(image_data)),
                    'Cache-Control': 'no-cache'
                }
            )
            logger.info("Response created successfully")
            return response
            
    except Exception as e:
        logger.error(f"Error in fetch_image: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Error fetching image: {str(e)}'}), 500

@history_bp.route('/cleanup_images', methods=['POST'])
def cleanup_images():
    try:
        max_age = int(request.args.get('max_age_hours', 24))
        result = cleanup_temp_images(max_age)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid max_age_hours parameter'}), 400
    except Exception as e:
        logger.error(f"Error in cleanup endpoint: {e}")
        return jsonify({'success': False, 'message': f'Cleanup failed: {str(e)}'}), 500

def cleanup_temp_images(max_age_hours=24):
    try:
        images_dir = 'images'
        if not os.path.exists(images_dir):
            return {'success': True, 'message': 'No images directory found', 'cleaned_files': 0}

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_files = 0

        for filename in os.listdir(images_dir):
            if filename.startswith('image_') and filename.endswith('.jpg'):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        try:
                            os.remove(filepath)
                            cleaned_files += 1
                        except Exception as e:
                            logger.warning(f"Could not remove {filepath}: {e}")

        return {
            'success': True,
            'message': f'Cleanup completed. Removed {cleaned_files} old image(s)',
            'cleaned_files': cleaned_files
        }
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {'success': False, 'message': f'Cleanup failed: {str(e)}', 'cleaned_files': 0}