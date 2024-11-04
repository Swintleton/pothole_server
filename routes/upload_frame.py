from flask import Blueprint, request, jsonify, g
from werkzeug.utils import secure_filename
from services.image_service import ImageService
from db.db_connection import Database
from utils.auth import Auth
from utils.logger import logger

upload_frame_bp = Blueprint('upload_frame', __name__)

@upload_frame_bp.route('/upload_frame', methods=['POST'])
def upload_frame():
    try:
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

        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file in request")
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = secure_filename(file.filename)
            try:
                file_path = ImageService.process_image(file, filename)
            except IOError:
                logger.error("Invalid image file type")
                return jsonify({'error': 'Invalid image file type'}), 400

            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')

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
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO uploaded_image 
                    (uploaded_image_user_id, uploaded_image_file_name, uploaded_image_created_datetime, 
                        uploaded_image_modified_datetime, uploaded_image_status_id, 
                        uploaded_image_gps_location_latitude, uploaded_image_gps_location_longitude) 
                    VALUES (%s, %s, NOW(), NOW(), 1, %s, %s)
                    """,
                    (g.user_id, filename, latitude, longitude)
                )
                conn.commit()
                cursor.close()
                Database.return_connection(conn)
            else:
                logger.error("Database connection failed")
                return jsonify({'error': 'Database connection failed'}), 500

        return jsonify({'message': 'Frame uploaded successfully'}), 200

    except Exception as e:
        logger.error(f"Error uploading frame: {e}")
        return jsonify({'error': 'Error uploading frame'}), 500
