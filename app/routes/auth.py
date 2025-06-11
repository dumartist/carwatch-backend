from flask import Blueprint, request, jsonify, session
import bleach
import logging

# Import utilities with fallback
try:
    from ..utils.database import get_db_connection
    from ..utils.auth import hash_password, check_password
except ImportError:
    # Fallback to root level
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils import get_db_connection, hash_password, check_password

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    try:
        with get_db_connection() as (db, cursor):
            username = bleach.clean(username)

            sql_check_user = "SELECT username FROM users WHERE username = %s"
            cursor.execute(sql_check_user, (username,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'Username already exists'}), 409

            hashed_password = hash_password(password)
            sql_insert_user = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(sql_insert_user, (username, hashed_password))
            db.commit()
            return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'message': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    try:
        with get_db_connection() as (db, cursor):
            username = bleach.clean(username)

            sql = "SELECT user_id, username, password FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

            if user and check_password(password, user['password']):
                session.permanent = True
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "user_id": user['user_id'],
                        "username": user['username']
                    }
                }), 200
            elif user:
                return jsonify({'success': False, 'message': 'Incorrect password'}), 401
            else:
                return jsonify({'success': False, 'message': 'Account not found'}), 404
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    return jsonify({
        'success': True,
        'message': 'User details retrieved successfully.',
        'data': {
            'user_id': session['user_id'],
            'username': session['username']
        }
    }), 200

@auth_bp.route('/update/username', methods=['POST'])
def update_username():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized. Please log in.'}), 401

    current_user_id = session['user_id']
    data = request.get_json(force=True)
    new_username = data.get('new_username')

    if not new_username:
        return jsonify({'success': False, 'message': 'New username is required'}), 400

    if not isinstance(new_username, str) or len(new_username) < 2:
        return jsonify({'success': False, 'message': 'New username must be a string of at least 2 characters'}), 400

    try:
        with get_db_connection() as (db, cursor):
            new_username = bleach.clean(new_username)

            # Check if new username is already taken
            sql_check_new_username = "SELECT user_id FROM users WHERE username = %s AND user_id != %s"
            cursor.execute(sql_check_new_username, (new_username, current_user_id))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'New username is already taken'}), 409

            # Update username
            sql_update_username = "UPDATE users SET username = %s WHERE user_id = %s"
            cursor.execute(sql_update_username, (new_username, current_user_id))
            db.commit()

            # Update session
            session['username'] = new_username
            return jsonify({
                'success': True,
                'message': 'Username updated successfully',
                'data': {
                    'new_username': new_username
                }
            }), 200

    except Exception as e:
        logger.error(f"Username update error: {e}")
        return jsonify({'success': False, 'message': 'Username update failed'}), 500

@auth_bp.route('/update/password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized. Please log in.'}), 401

    current_user_id = session['user_id']
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_new_password = data.get('confirm_new_password')

    if not all([current_password, new_password, confirm_new_password]):
        return jsonify({'success': False, 'message': 'Current password, new password, and confirmation are required'}), 400

    if new_password != confirm_new_password:
        return jsonify({'success': False, 'message': 'New password and confirmation do not match'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters long'}), 400

    try:
        with get_db_connection() as (db, cursor):
            # Verify current password
            sql_get_user = "SELECT password FROM users WHERE user_id = %s"
            cursor.execute(sql_get_user, (current_user_id,))
            user_data = cursor.fetchone()

            if not user_data or not check_password(current_password, user_data['password']):
                return jsonify({'success': False, 'message': 'Incorrect current password'}), 403

            # Update password
            hashed_new_password = hash_password(new_password)
            sql_update_password = "UPDATE users SET password = %s WHERE user_id = %s"
            cursor.execute(sql_update_password, (hashed_new_password, current_user_id))
            db.commit()

            return jsonify({'success': True, 'message': 'Password updated successfully'}), 200

    except Exception as e:
        logger.error(f"Password update error: {e}")
        return jsonify({'success': False, 'message': 'Password update failed'}), 500

@auth_bp.route('/delete', methods=['POST'])
def delete_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized. Please log in.'}), 401

    current_user_id = session['user_id']
    data = request.get_json()
    password_for_verification = data.get('password')

    if not password_for_verification:
        return jsonify({'success': False, 'message': 'Password is required for verification'}), 400

    try:
        with get_db_connection() as (db, cursor):
            # Verify password
            sql_get_user = "SELECT password FROM users WHERE user_id = %s"
            cursor.execute(sql_get_user, (current_user_id,))
            user_data = cursor.fetchone()

            if not user_data or not check_password(password_for_verification, user_data['password']):
                return jsonify({'success': False, 'message': 'Incorrect password. Account deletion failed.'}), 403

            # Delete associated history records first (if user_id column exists)
            try:
                sql_delete_history = "DELETE FROM history WHERE user_id = %s"
                cursor.execute(sql_delete_history, (current_user_id,))
            except Exception:
                # If user_id column doesn't exist in history table, skip this step
                logger.info("History table doesn't have user_id column, skipping history cleanup")

            # Delete user
            sql_delete_user = "DELETE FROM users WHERE user_id = %s"
            cursor.execute(sql_delete_user, (current_user_id,))
            db.commit()

            # Clear session
            session.pop('user_id', None)
            session.pop('username', None)

            return jsonify({'success': True, 'message': 'Account deleted successfully'}), 200

    except Exception as e:
        logger.error(f"Account deletion error: {e}")
        return jsonify({'success': False, 'message': 'Account deletion failed'}), 500
