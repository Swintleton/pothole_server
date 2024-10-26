from utils.logger import logger
from flask import Blueprint, request, jsonify
from db.db_connection import Database
from utils.auth import Auth

pothole_bp = Blueprint('pothole', __name__)

@pothole_bp.route('/add_pothole', methods=['POST'])
def add_pothole():
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

    auth = Auth(token)  # Pass token to Auth class

    if not auth.verify_token():
        logger.error("Token verification failed")
        return jsonify({'error': 'Unauthorized'}), 401

    # Extract the user_id from the token
    user_id = auth.get_user_id_from_token()
    if user_id is None:
        logger.error("User ID extraction failed")
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not latitude or not longitude:
        return jsonify({"error": "Invalid coordinates"}), 400

    conn = Database.get_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # Default filename
        filename = "manual_entry.jpg"

        cursor.execute("""
            INSERT INTO uploaded_image (uploaded_image_user_id, uploaded_image_file_name, 
                                        uploaded_image_created_datetime, uploaded_image_modified_datetime, 
                                        uploaded_image_status_id, uploaded_image_gps_location_latitude, 
                                        uploaded_image_gps_location_longitude) 
            VALUES (%s, %s, NOW(), NOW(), 3, %s, %s)
            RETURNING uploaded_image_id
        """, (user_id, filename, latitude, longitude))  # Use real user_id and default values
        
        pothole_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        Database.return_connection(conn)

        # Return the pothole id and filename
        return jsonify({"id": pothole_id, "filename": filename}), 200
    except Exception as e:
        logger.info(f"Error adding pothole: {e}")
        return jsonify({"error": "Error adding pothole"}), 500

@pothole_bp.route('/edit_pothole/<int:id>', methods=['PUT'])
def edit_pothole(id):
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not latitude or not longitude:
        return jsonify({"error": "Invalid coordinates"}), 400

    conn = Database.get_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE uploaded_image
            SET uploaded_image_gps_location_latitude = %s, 
                uploaded_image_gps_location_longitude = %s,
                uploaded_image_modified_datetime = NOW()
            WHERE uploaded_image_id = %s
        """, (latitude, longitude, id))
        conn.commit()
        cursor.close()
        Database.return_connection(conn)
        return jsonify({"message": "Pothole updated successfully"}), 200
    except Exception as e:
        logger.info(f"Error updating pothole: {e}")
        return jsonify({"error": "Error updating pothole"}), 500
