from flask import Blueprint, jsonify, request
from db.db_connection import Database
from utils.auth import Auth
from utils.logger import logger
from services.detection_service import DetectionService
from datetime import datetime, timedelta

get_detection_confirmation_bp = Blueprint('get_detection_confirmation', __name__)

@get_detection_confirmation_bp.route('/get_detection_confirmation', methods=['GET'])
def get_detection_confirmation():
    auth_token = request.headers.get('Authorization')

    if not auth_token:
        return jsonify({'error': 'Unauthorized'}), 401

    if not auth_token.startswith("Bearer "):
        return jsonify({'error': 'Invalid token format'}), 401

    try:
        token = auth_token.split(" ")[1]
    except IndexError:
        return jsonify({'error': 'Invalid token'}), 401

    auth = Auth(token)
    if not auth.verify_token():
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = auth.get_user_id_from_token()

    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Define the threshold for 30 seconds ago
        threshold_time = datetime.now() - timedelta(seconds=30)

        # Select frames older than 30 seconds for deletion
        cursor.execute("""
            SELECT uploaded_image_id, uploaded_image_file_name
            FROM uploaded_image
            WHERE uploaded_image_status_id = 2
            AND uploaded_image_modified_datetime < %s
        """, (threshold_time,))

        old_frames = cursor.fetchall()
        
        # Delete each old frame found
        for frame in old_frames:
            image_id, filename = frame  # Ensure frame is treated as tuple here
            DetectionService.delete_image_and_record(image_id, filename)

        # Fetch the first detection awaiting confirmation for the user
        cursor.execute("""
            SELECT uploaded_image_id, uploaded_image_file_name
            FROM uploaded_image
            WHERE uploaded_image_status_id = 2 AND uploaded_image_user_id = %s
            LIMIT 1
        """, (user_id,))
        
        pending_detection = cursor.fetchone()

        cursor.close()
        Database.return_connection(conn)

        if pending_detection:
            detection = {"image_id": pending_detection[0], "filename": pending_detection[1].replace(".jpg", "_detected.jpg")}
            return jsonify(detection), 200
        else:
            # No pending detections found
            return jsonify({'message': 'No pending detections'}), 200
    except Exception as e:
        logger.error(f"Error fetching detection confirmation: {e}")
        return jsonify({'error': 'Server error'}), 500
