from flask import Blueprint, request, jsonify
from db.db_connection import Database

pothole_bp = Blueprint('pothole', __name__)

@pothole_bp.route('/add_pothole', methods=['POST'])
def add_pothole():
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
            INSERT INTO uploaded_image (uploaded_image_user_id, uploaded_image_file_name, 
                                        uploaded_image_created_datetime, uploaded_image_modified_datetime, 
                                        uploaded_image_status_id, uploaded_image_gps_location_latitude, 
                                        uploaded_image_gps_location_longitude) 
            VALUES (%s, %s, NOW(), NOW(), 3, %s, %s)
        """, (1, 'manual_entry', latitude, longitude))  # Use real user_id and default values
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Pothole added successfully"}), 200
    except Exception as e:
        print(f"Error adding pothole: {e}")
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
        conn.close()
        return jsonify({"message": "Pothole updated successfully"}), 200
    except Exception as e:
        print(f"Error updating pothole: {e}")
        return jsonify({"error": "Error updating pothole"}), 500
