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

    auth = Auth(token)

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

    # Check if latitude and longitude exist
    if latitude is None or longitude is None:
        return jsonify({"error": "Invalid coordinates"}), 400
    
    # Check if latitude and longitude are numbers
    try:
        test_latitude = float(latitude)
        test_longitude = float(longitude)
    except (TypeError, ValueError):
        return jsonify({"error": "Coordinates must be numbers"}), 400
    
    # Check if latitude is between -90 and 90, and longitude is between -180 and 180
    if not (-90 <= float(latitude) <= 90 and -180 <= float(longitude) <= 180):
        return jsonify({"error": "Coordinates are out of bounds"}), 400

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

    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not latitude or not longitude:
        return jsonify({"error": "Invalid coordinates"}), 400
    
    # Extract user ID and role ID
    user_id = auth.get_user_id_from_token()
    user_role = auth.get_user_role()

    conn = Database.get_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT uploaded_image_user_id FROM uploaded_image WHERE uploaded_image_id = %s
        """, (id,))
        pothole = cursor.fetchone()

        if pothole:
            pothole_creator_id = pothole[0]
            # Check if user is either the creator or an admin
            if user_id == pothole_creator_id or user_role == 'Admin':
                cursor.execute("""
                    UPDATE uploaded_image
                    SET uploaded_image_gps_location_latitude = %s, 
                        uploaded_image_gps_location_longitude = %s,
                        uploaded_image_modified_datetime = NOW()
                    WHERE uploaded_image_id = %s
                """, (latitude, longitude, id))
                conn.commit()
                logger.info(f"Pothole {id} updated by user {user_id}")
                return jsonify({"message": "Pothole updated successfully"}), 200
            else:
                logger.warning(f"Unauthorized edit attempt by user {user_id}")
                return jsonify({"error": "Unauthorized"}), 403
    except Exception as e:
        logger.info(f"Error updating pothole: {e}")
        return jsonify({"error": "Error updating pothole"}), 500
    finally:
        cursor.close()
        Database.return_connection(conn)

@pothole_bp.route('/delete_pothole/<int:id>', methods=['DELETE'])
def delete_pothole(id):
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

    # Extract user ID and role ID
    user_id = auth.get_user_id_from_token()
    user_role = auth.get_user_role()

    conn = Database.get_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT uploaded_image_user_id FROM uploaded_image WHERE uploaded_image_id = %s
        """, (id,))
        pothole = cursor.fetchone()

        if pothole:
            pothole_creator_id = pothole[0]
            # Check if user is either the creator or an admin
            if user_id == pothole_creator_id or user_role == 'Admin':
                cursor.execute("DELETE FROM uploaded_image WHERE uploaded_image_id = %s", (id,))
                conn.commit()
                logger.info(f"Pothole {id} deleted by user {user_id}")
                return jsonify({"message": "Pothole deleted successfully"}), 200
            else:
                logger.warning(f"Unauthorized delete attempt by user {user_id}")
                return jsonify({"error": "Unauthorized"}), 403
        else:
            return jsonify({"error": "Pothole not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting pothole: {e}")
        return jsonify({"error": "Error deleting pothole"}), 500
    finally:
        cursor.close()
        Database.return_connection(conn)
