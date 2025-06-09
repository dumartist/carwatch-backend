from flask import Blueprint, request, jsonify, session
import bleach
import os
import cv2
import numpy as np
import datetime
import logging
from ..services.db_upload import db_upload_image

# Import utilities with fallback
try:
    from ..utils.database import get_db_connection
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils import get_db_connection

# OCR imports with fallback
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

@history_bp.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image part in the request'}), 400

    file = request.files['image']
    status = request.args.get('status', 'unknown') 

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    if file:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1]
        filename = f"image_{timestamp}{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        image_bytes = file.read()
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        logger.info(f"Image saved temporarily to {filepath} with status '{status}'")

        # Upload to database FIRST, before OCR processing
        db_upload_result = db_upload_image(filename)
        if db_upload_result['success']:
            logger.info(f"Image uploaded to database: {db_upload_result['message']}")
        else:
            logger.warning(f"Failed to upload image to database: {db_upload_result['message']}")

        try:
            img_np = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            if img_np is None:
                raise ValueError("Could not decode image.")
        except Exception as e:
            os.remove(filepath) 
            return jsonify({'success': False, 'message': f'Error decoding image: {e}'}), 500

        # Process OCR after database upload
        cropped_plate = detect_and_crop_plate(img_np)
        plate_number = ""
        if cropped_plate is not None:
            plate_number = recognize_characters_with_yolo(cropped_plate)
            logger.info(f"OCR Result: {plate_number}")
        else:
            logger.info("OCR could not be performed as no plate was detected.")

        description = "car is available" if status == "entering" else "car is being use"
        subject = "Vehicle Entry" if status == "entering" else ("Vehicle Exit" if status == "leaving" else "Unknown Status")

        try:
            with get_db_connection() as (db, cursor):
                sql = "INSERT INTO history (plate, subject, description) VALUES (%s, %s, %s)"
                val = (plate_number, subject, description)
                cursor.execute(sql, val)
                db.commit()
                message = 'Image received, uploaded to database, OCR processed, and data recorded successfully.'
                status_code = 201
        except Exception as e:
            logger.error(f"Database recording error: {e}")
            message = f'Failed to record data to database: {e}'
            status_code = 500
        finally:
            # Clean up temporary file
            os.remove(filepath)

        response_data = {
            'success': status_code == 201, 
            'message': message, 
            'plate_number': plate_number, 
            'status': status
        }
        
        # Include database upload status in response
        if db_upload_result['success']:
            response_data['image_uploaded'] = True
            response_data['image_filename'] = db_upload_result['filename']
        else:
            response_data['image_uploaded'] = False
            response_data['upload_error'] = db_upload_result['message']

        return jsonify(response_data), status_code
    
    return jsonify({'success': False, 'message': 'Something went wrong.'}), 500

@history_bp.route('/history', methods=['GET'])
def get_all_history():
    try:
        with get_db_connection() as (db, cursor):
            # Check if user_id column exists in history table
            try:
                sql = """SELECT h.subject, h.plate, h.description, h.date, u.username 
                        FROM history h 
                        LEFT JOIN users u ON h.user_id = u.user_id 
                        ORDER BY h.date DESC"""
                cursor.execute(sql)
                history_data = cursor.fetchall()
            except Exception:
                # Fallback to original query if user_id column doesn't exist
                sql = "SELECT subject, plate, description, date FROM history ORDER BY date DESC"
                cursor.execute(sql)
                history_data = cursor.fetchall()
            
            return jsonify({'success': True, 'message': 'History retrieved', 'data': history_data}), 200
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'success': False, 'message': 'Error fetching history'}), 500

@history_bp.route('/plate', methods=['POST'])
def record_plate():
    data = request.get_json()
    plate = data.get('plate')
    subject = data.get('subject')
    description = data.get('description')

    if not all([plate, subject, description]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Get user_id from session if available
    user_id = session.get('user_id', None)

    try:
        with get_db_connection() as (db, cursor):
            # Try to insert with user_id first
            try:
                sql = "INSERT INTO history (plate, subject, description, user_id) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (bleach.clean(plate), bleach.clean(subject), bleach.clean(description), user_id))
            except Exception:
                # Fallback to original schema without user_id
                sql = "INSERT INTO history (plate, subject, description) VALUES (%s, %s, %s)"
                cursor.execute(sql, (bleach.clean(plate), bleach.clean(subject), bleach.clean(description)))
            
            db.commit()
            return jsonify({'success': True, 'message': 'Plate recorded successfully'}), 201
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Recording failed'}), 500