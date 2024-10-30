from flask import Blueprint, request, jsonify
from db.db_connection import Database
import bcrypt
import re

registration_bp = Blueprint('registration', __name__)

# Regular expressions for format checks
EMAIL_REGEX = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
PHONE_REGEX = r'^\+?[0-9\s\-\(\)]{10,15}$'
PASSWORD_REGEX = r'^(?=.*?[0-9])(?=.*?[!@#\$&*~]).{8,}$'

@registration_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    login = data.get('login')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phone')

    # Check if required fields are provided
    if not username or not login or not password or not email:
        return jsonify({'error': 'Username, login, password, and email are required'}), 400

    # Validate email format
    if not re.match(EMAIL_REGEX, email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Validate phone format if provided
    if phone and not re.match(PHONE_REGEX, phone):
        return jsonify({'error': 'Invalid phone number format'}), 400

    # Validate password strength
    if not re.match(PASSWORD_REGEX, password):
        return jsonify({
            'error': 'Password must be at least 8 characters, include a number, and a special character'
        }), 400

    # Connect to the database
    conn = Database.get_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    # Check if the login already exists
    cursor.execute("SELECT user_id FROM \"user\" WHERE user_login = %s", (login,))
    if cursor.fetchone():
        cursor.close()
        Database.return_connection(conn)
        return jsonify({'error': 'Login already exists'}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Insert new user with the Reporter role (user_role_id = 2)
    try:
        cursor.execute(
            """
            INSERT INTO "user" (
                user_name, user_login, user_password, user_role_id, 
                user_created_datetime, user_email, user_phone_number
            ) VALUES (%s, %s, %s, 2, NOW(), %s, %s)
            """,
            (username, login, hashed_password, email, phone)
        )
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': 'Registration failed'}), 500
    finally:
        cursor.close()
        Database.return_connection(conn)
