from flask import Flask, request, Blueprint, jsonify
import bcrypt
from db.db_connection import Database
from flask_jwt_extended import create_access_token, JWTManager

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Connect to the database
    conn = Database.get_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    # Query the database for the user
    cursor.execute("SELECT user_id, user_password FROM \"user\" WHERE user_login = %s", (username,))
    result = cursor.fetchone()

    if result:
        user_id, stored_password = result

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

            return jsonify({"message": "Login successful", "auth_token": bearer_token}), 200
        else:
            cursor.close()
            Database.return_connection(conn)
            return jsonify({"error": "Invalid username or password"}), 401
    else:
        cursor.close()
        Database.return_connection(conn)
        return jsonify({"error": "Invalid username or password"}), 401
