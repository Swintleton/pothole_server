from utils.logger import logger
from flask import Blueprint, request, jsonify
from db.db_connection import Database
import os
from utils.auth import Auth

pothole_coordinates_bp = Blueprint('pothole_coordinates', __name__)

@pothole_coordinates_bp.route('/potholes', methods=['GET'])
def get_pothole_coordinates():
    auth_token = request.headers.get('Authorization')

    if not auth_token:
        logger.error("Authorization header is missing")
        return jsonify({'error': 'Unauthorized'}), 401

    # Ensure the header contains a "Bearer" token
    if not auth_token.startswith("Bearer "):
        logger.error("Authorization header format is invalid")
        return jsonify({'error': 'Unauthorized'}), 401

    # Try to extract the token part
    try:
        token = auth_token.split(" ")[1]
    except IndexError:
        logger.error("Token not found in Authorization header")
        return jsonify({'error': 'Unauthorized'}), 401

    auth = Auth(token)

    if not auth.verify_token():
        logger.error("Token verification failed")
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = Database.get_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        cursor.execute("""
            SELECT uploaded_image_id, uploaded_image_gps_location_latitude, 
                   uploaded_image_gps_location_longitude, uploaded_image_file_name, 
                   uploaded_image_user_id
            FROM uploaded_image
            WHERE uploaded_image_status_id = 3
        """)
        potholes = cursor.fetchall()

        cursor.close()
        Database.return_connection(conn)

        # Format the results into a list of dictionaries
        coordinates = [
            {
                "id": row[0],
                "latitude": row[1],
                "longitude": row[2],
                "filename": os.path.splitext(row[3])[0] + "_detected.jpg",
                "user_id": row[4]
            } for row in potholes
        ]

        return jsonify(coordinates), 200
    except Exception as e:
        logger.error(f"Error fetching pothole coordinates: {e}")
        return jsonify({"error": "Error fetching coordinates"}), 500
