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
    Upload image from uploads directory to MySQL database as MEDIUMBLOB,
    using a stored procedure to first clear old images and then insert the new one.
    This optimizes the process by reducing network roundtrips and centralizing logic.

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
            # Convert to RGB if necessary for consistent saving
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
                format_type = 'JPEG' # Use JPEG for RGB conversion output
            else:
                # Use original format if available, otherwise default to PNG
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

        # Save to database using stored procedure
        try:
            with get_db_connection() as (db, cursor):
                # Call the stored procedure to clear old images and insert the new one.
                # The stored procedure handles the DELETE and INSERT as one atomic operation.
                sql_call_procedure = "CALL insert_and_clear_images(%s, %s, %s, %s)"
                values = (
                    image_filename,
                    img_data,
                    file_size,
                    file_extension
                )
                try:
                    cursor.execute(sql_call_procedure, values)
                    db.commit()

                    # After calling a stored procedure that modifies the table, cursor.lastrowid
                    # might not directly return the ID of the newly inserted row in MySQL Connector/Python.
                    # For this "single image" use case, confirming success is usually sufficient.
                    logger.info(f"Successfully uploaded {image_filename} as {format_type} ({file_size} bytes) via stored procedure.")
                    return {
                        'success': True,
                        'message': f'Image uploaded successfully via stored procedure as {format_type}',
                        'filename': image_filename,
                        'file_size': file_size
                    }

                except mysql.connector.Error as db_error:
                    # If images table or procedure doesn't exist, try to create them
                    # Note: For production, ensure your stored procedure is deployed reliably.
                    # This fallback is primarily for development/initial setup.
                    if ("doesn't exist" in str(db_error).lower() and "table" in str(db_error).lower()) or \
                       ("PROCEDURE insert_and_clear_images does not exist" in str(db_error)):
                        logger.warning(f"Database setup issue (Error: {db_error}). Attempting to create table (and assuming procedure creation is handled elsewhere).")
                        try:
                            # Create the table if it's missing (ensure it has image_id as PK)
                            create_images_table(cursor, db)
                            
                            # Log that the stored procedure also needs to be created manually or via deployment script
                            logger.warning("The 'insert_and_clear_images' stored procedure might also need to be created manually in your database if this is the first run.")
                            logger.info(f"Retrying upload for {image_filename} after table creation.")
                            
                            # Retry the call to the stored procedure
                            cursor.execute(sql_call_procedure, values)
                            db.commit()

                            logger.info(f"Successfully uploaded {image_filename} after table creation and retry.")

                            return {
                                'success': True,
                                'message': f'Image uploaded successfully (table created and retried)',
                                'filename': image_filename,
                                'file_size': file_size
                            }
                        except Exception as create_error:
                            logger.error(f"Failed to create images table or retry upload: {create_error}")
                            db.rollback() # Rollback if table creation or retry fails
                            return {'success': False, 'message': f'Database table creation or retry upload failed: {create_error}'}
                    else:
                        logger.error(f"Database error during image upload via stored procedure: {db_error}")
                        db.rollback() # Rollback on other SQL errors
                        return {'success': False, 'message': f'Database error: {str(db_error)}'}
        except ImportError as import_error:
            logger.error(f"Database connection import error: {import_error}")
            return {'success': False, 'message': 'Database connection not available'}
        except Exception as conn_error:
            logger.error(f"Database connection error: {conn_error}")
            return {'success': False, 'message': f'Database connection failed: {str(conn_error)}'}

    except FileNotFoundError:
        logger.error(f"Image file not found at path: {image_path}")
        return {'success': False, 'message': f'Image file not found at path: {image_path}'}
    except Exception as e:
        logger.error(f"Error processing or uploading image {image_filename}: {e}", exc_info=True)
        return {'success': False, 'message': f'Upload failed: {str(e)}'}

def create_images_table(cursor, db):
    """Create the images table with a primary key."""
    sql = """
    CREATE TABLE images (
        image_id INT AUTO_INCREMENT PRIMARY KEY, -- Ensure image_id is the primary key
        filename VARCHAR(255) NOT NULL,
        image_data MEDIUMBLOB NOT NULL,
        file_size INT NOT NULL,
        file_type VARCHAR(10) NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_filename (filename),
        INDEX idx_upload_date (upload_date)
    )
    """
    try:
        cursor.execute(sql)
        db.commit()
        logger.info("Images table created successfully")
    except Exception as e:
        logger.error(f"Error creating images table: {e}")
        db.rollback()
        raise # Re-raise exception to be caught by caller
