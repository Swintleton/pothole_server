from flask import Flask, request, Blueprint, jsonify
import bcrypt
from db.db_connection import Database
from utils.auth import Auth

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
    cursor.execute("SELECT user_password FROM \"user\" WHERE user_login = %s", (username,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        stored_password = result[0]

        # Verify the provided password with the stored hashed password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            # For now, returning a fake token, replace this with real token generation logic
            return jsonify({"message": "Login successful", "auth_token": "fake_token"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    else:
        return jsonify({"error": "Invalid username or password"}), 401
