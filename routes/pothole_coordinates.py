from flask import Blueprint, jsonify
from db.db_connection import Database

pothole_coordinates_bp = Blueprint('pothole_coordinates', __name__)

@pothole_coordinates_bp.route('/potholes', methods=['GET'])
def get_pothole_coordinates():
    try:
        conn = Database.get_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        cursor.execute("""
            SELECT uploaded_image_id, uploaded_image_gps_location_latitude, uploaded_image_gps_location_longitude
            FROM uploaded_image
            WHERE uploaded_image_status_id = 3
        """)
        potholes = cursor.fetchall()

        cursor.close()
        conn.close()

        # Format the results into a list of dictionaries
        coordinates = [
            {
                "id": row[0],
                "latitude": row[1],
                "longitude": row[2]
            } for row in potholes
        ]

        return jsonify(coordinates), 200
    except Exception as e:
        print(f"Error fetching pothole coordinates: {e}")
        return jsonify({"error": "Error fetching coordinates"}), 500
