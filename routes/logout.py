from utils.logger import logger
from flask import Blueprint, jsonify, request
from db.db_connection import Database
from flask_jwt_extended import decode_token, create_access_token
from datetime import timedelta

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout', methods=['POST'])
def logout():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Logout failed"}), 401

        # Extract the token from the header
        token = auth_header.split(" ")[1]

        try:
            decoded_token = decode_token(token)
            user_id = decoded_token.get("sub")  # "sub" is the user_id in the token payload

            if not user_id:
                return jsonify({"message": "Logout failed"}), 401

            # Generate an expired token to overwrite the user's token
            expired_token = 'Bearer ' + create_access_token(identity=user_id, expires_delta=timedelta(seconds=-1))

            conn = Database.get_connection()
            if conn is None:
                logger.error("Database connection failed during logout.")
                return jsonify({"error": "Database connection failed"}), 500

            cursor = conn.cursor()

            # Update the user's auth token to the expired token
            cursor.execute(
                "UPDATE \"user\" SET user_auth_token = %s WHERE user_id = %s",
                (expired_token, user_id)
            )
            conn.commit()
            return jsonify({"message": "Logout successful"}), 200
        except Exception as e:
            logger.error(f"Token decoding failed during logout: {e}")
            return jsonify({'error': 'Invalid token'}), 401
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                Database.return_connection(conn)

    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")
        return jsonify({'error': 'Error during logout'}), 500
