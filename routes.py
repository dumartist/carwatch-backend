from flask import Flask, request, jsonify, session
import utils
import config
import bleach

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

@app.route('/')
def hello_world():
    return 'Hello World!'

#========================= User Routes =========================

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    db = utils.connect_to_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    cursor = db.cursor()
    try:
        # Sanitize username
        username = bleach.clean(username)

        sql_check_user = "SELECT username FROM users WHERE username = %s"
        cursor.execute(sql_check_user, (username,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Username already exists'}), 409

        hashed_password = utils.hash_password(password)
        sql_insert_user = "INSERT INTO users (username, password) VALUES (%s, %s)"
        val = (username, hashed_password)
        cursor.execute(sql_insert_user, val)
        db.commit()
        return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Registration failed: An internal error occurred.'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    db = utils.connect_to_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    try:
        # Sanitize username
        username = bleach.clean(username)

        sql = "SELECT user_id, username, password FROM users WHERE username = %s"
        val = (username,)
        cursor.execute(sql, val)
        user = cursor.fetchone()

        if user and utils.check_password(password, user['password']):
            session['user_id'] = user['user_id'] # Store user_id in session
            session['username'] = user['username'] # Store username in session
            response = {
                "success": True,
                "message": "Login successful",
                "data": {
                    "user_id": user['user_id'],
                    "username": user['username']
                }
            }
            return jsonify(response), 200
        elif user:
            return jsonify({'success': False, 'message': 'Incorrect password'}), 401
        else:
            return jsonify({'success': False, 'message': 'Account not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login failed: An internal error occurred.'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@app.route('/user/update/username', methods=['POST'])
def update_username():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized. Please log in.'}), 401

    current_user_id = session['user_id']
    data = request.get_json()
    new_username = data.get('new_username')
    password_for_verification = data.get('password')

    if not new_username or not password_for_verification:
        return jsonify({'success': False, 'message': 'New username and current password are required'}), 400

    if not isinstance(new_username, str) or len(new_username) < 2:
        return jsonify({'success': False, 'message': 'New username must be a string of at least 2 characters'}), 400

    db = utils.connect_to_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    try:
        # Sanitize new_username
        new_username = bleach.clean(new_username)

        # Verify current password
        sql_get_user = "SELECT password FROM users WHERE user_id = %s"
        cursor.execute(sql_get_user, (current_user_id,))
        user_data = cursor.fetchone()

        if not user_data or not utils.check_password(password_for_verification, user_data['password']):
            return jsonify({'success': False, 'message': 'Incorrect current password'}), 403

        # Check if new username is already taken by another user
        sql_check_new_username = "SELECT user_id FROM users WHERE username = %s AND user_id != %s"
        cursor.execute(sql_check_new_username, (new_username, current_user_id))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'New username is already taken'}), 409

        # Update username
        sql_update_username = "UPDATE users SET username = %s WHERE user_id = %s"
        cursor.execute(sql_update_username, (new_username, current_user_id))
        db.commit()

        session['username'] = new_username
        return jsonify({
            'success': True,
            'message': 'Username updated successfully',
            'data': {
                'new_username': new_username
            }
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Username update failed: An internal error occurred.'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/user/update/password', methods=['POST'])
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

    if len(new_password) < 6: # Basic password length validation
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters long'}), 400

    db = utils.connect_to_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    try:
        # Verify current password
        sql_get_user = "SELECT password FROM users WHERE user_id = %s"
        cursor.execute(sql_get_user, (current_user_id,))
        user_data = cursor.fetchone()

        if not user_data or not utils.check_password(current_password, user_data['password']):
            return jsonify({'success': False, 'message': 'Incorrect current password'}), 403

        # Hash the new password and update
        hashed_new_password = utils.hash_password(new_password)
        sql_update_password = "UPDATE users SET password = %s WHERE user_id = %s"
        cursor.execute(sql_update_password, (hashed_new_password, current_user_id))
        db.commit()

        return jsonify({'success': True, 'message': 'Password updated successfully'}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Password update failed: An internal error occurred.'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/user/delete', methods=['POST'])
def delete_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized. Please log in.'}), 401

    current_user_id = session['user_id']
    data = request.get_json()
    password_for_verification = data.get('password')

    if not password_for_verification:
        return jsonify({'success': False, 'message': 'Password is required for verification'}), 400

    db = utils.connect_to_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    try:
        # Verify current password
        sql_get_user = "SELECT password FROM users WHERE user_id = %s"
        cursor.execute(sql_get_user, (current_user_id,))
        user_data = cursor.fetchone()

        if not user_data or not utils.check_password(password_for_verification, user_data['password']):
            return jsonify({'success': False, 'message': 'Incorrect password. Account deletion failed.'}), 403

        # Delete associated history records first to maintain referential integrity
        # (Assuming no ON DELETE CASCADE is set up at the database level for history.user_id)
        sql_delete_history = "DELETE FROM history WHERE user_id = %s"
        cursor.execute(sql_delete_history, (current_user_id,))
        
        # Delete the user
        sql_delete_user = "DELETE FROM users WHERE user_id = %s"
        cursor.execute(sql_delete_user, (current_user_id,))
        db.commit()

        # Clear session after successful deletion
        session.pop('user_id', None)
        session.pop('username', None)

        return jsonify({'success': True, 'message': 'Account deleted successfully'}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Account deletion failed: An internal error occurred.'}), 500
    finally:
        cursor.close()
        db.close()

#========================= History Routes =========================

@app.route('/history', methods=['POST'])
def record_plate():
    # For consistency and security, this route should also use session for user_id
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized. Please log in to record history.'}), 401

    current_user_id = session['user_id']
    data = request.get_json()
    plate = data.get('plate')
    subject = data.get('subject')  # e.g., "Entry" or "Exit"
    description = data.get('description')

    if not all([plate, subject, description]): # user_id check removed as it's from session
         return jsonify({'success': False, 'message': 'Missing plate, subject, or description'}), 400

    # Sanitize inputs
    plate = bleach.clean(plate)
    subject = bleach.clean(subject)
    description = bleach.clean(description)

    db = utils.connect_to_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    cursor = db.cursor()
    try:
        sql = "INSERT INTO history (user_id, plate, subject, description) VALUES (%s, %s, %s, %s)"
        val = (current_user_id, plate, subject, description)
        cursor.execute(sql, val)
        db.commit()
        return jsonify({'success': True, 'message': 'Plate recorded successfully'}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Recording failed: An internal error occurred.'}), 500
    finally:
        cursor.close()
        db.close()

@app.route('/history', methods=['GET'])
def get_all_history():
    db = utils.connect_to_db()
    if not db:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500

    cursor = db.cursor(dictionary=True)
    try:
        sql = "SELECT subject, plate, description, date FROM history ORDER BY date DESC"
        cursor.execute(sql)
        history_data = cursor.fetchall()
        return jsonify({'success': True, 'message': 'History retrieved successfully', 'data': history_data}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching history: {str(e)}'}), 500
    finally:
        cursor.close()
        db.close()