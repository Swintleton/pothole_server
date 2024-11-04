from flask import Flask, request, Blueprint, jsonify
import bcrypt
from db.db_connection import Database
from flask_jwt_extended import create_access_token, JWTManager
import re

login_bp = Blueprint('login', __name__)

USERNAME_REGEX = r'^[a-zA-Z0-9\_\-]+$'

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Validate username format
    if not re.match(USERNAME_REGEX, username):
        return jsonify({'error': 'Invalid username format'}), 400

    # Check the length of username and password
    if len(username) > 128:
        return jsonify({'error': 'Username too long'}), 400
    if len(password) > 256:
        return jsonify({'error': 'Password too long'}), 400

    # Connect to the database
    conn = Database.get_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    # Query the database for the user along with their role
    cursor.execute("""
        SELECT u.user_id, u.user_password, r.user_role_name 
        FROM "user" u
        INNER JOIN user_role r ON u.user_role_id = r.user_role_id
        WHERE u.user_login = %s
    """, (username,))
    result = cursor.fetchone()

    if result:
        user_id, stored_password, user_role = result

        # Verify the provided password with the stored hashed password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            # Generate JWT token
            access_token = create_access_token(identity=user_id)  # Return a JWT token
            bearer_token = f"Bearer {access_token}"  # Add "Bearer " prefix

            # Update the user's auth token in the database
            try:
                cursor.execute(
                    "UPDATE \"user\" SET user_auth_token = %s WHERE user_id = %s",
                    (bearer_token, user_id)
                )
                conn.commit()
            except Exception as e:
                conn.rollback()  # Rollback if there's an error
                return jsonify({"error": "Failed to update auth token"}), 500
            finally:
                cursor.close()
                Database.return_connection(conn)

            # Return both the auth token and the user's role
            return jsonify({
                "message": "Login successful",
                "auth_token": bearer_token,
                "user_id": user_id,
                "user_role": user_role
            }), 200
        else:
            cursor.close()
            Database.return_connection(conn)
            return jsonify({"error": "Invalid username or password"}), 401
    else:
        cursor.close()
        Database.return_connection(conn)
        return jsonify({"error": "Invalid username or password"}), 401
