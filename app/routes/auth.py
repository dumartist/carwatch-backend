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
        'data': {
            'user_id': session['user_id'],
            'username': session['username']
        }
    }), 200
