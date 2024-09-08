from flask import Blueprint, request, jsonify, g
from werkzeug.utils import secure_filename
from services.image_service import ImageService
from db.db_connection import Database
from utils.auth import Auth

upload_frame_bp = Blueprint('upload_frame', __name__)

@upload_frame_bp.route('/upload_frame', methods=['POST'])
def upload_frame():
    try:
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify({'error': 'Unauthorized'}), 401

        token = auth_token.split(" ")[1]
        auth = Auth(token)

        if not auth.verify_token():
            return jsonify({'error': 'Unauthorized'}), 401

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = secure_filename(file.filename)
            file_path = ImageService.process_image(file, filename)

            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')

            if latitude and longitude:
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
                    conn.close()
                else:
                    return jsonify({'error': 'Database connection failed'}), 500

        return ('', 204)

    except Exception as e:
        print(f"Error uploading frame: {e}")
        return jsonify({'error': 'Error uploading frame'}), 500
