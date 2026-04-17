from flask import Blueprint, request, jsonify
from utils.logger import logger
from db.db_connection import Database
from services.detection_service import DetectionService
from utils.auth import Auth

confirm_bp = Blueprint('confirm', __name__)

@confirm_bp.route('/confirm', methods=['POST'])
def confirm_detection():
    """
    Confirm detection based on filename and confirmation status provided by the client.
    """
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

    # Parse the JSON payload
    data = request.get_json()
    filename = data.get('filename')
    confirmed = data.get('confirmed', False)
    
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    # Find the image ID by filename
    conn = Database.get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT uploaded_image_id FROM uploaded_image WHERE uploaded_image_file_name = %s", (filename,))
        result = cursor.fetchone()

        if result:
            image_id = result[0]
            if confirmed:
                # Confirm detection
                DetectionService.confirm_detection(image_id, filename)
                return jsonify({'message': 'Detection confirmed'}), 200
            else:
                # Reject detection and delete the image/record
                DetectionService.delete_image_and_record(image_id, filename)
                return jsonify({'message': 'Detection rejected and deleted'}), 200
        else:
            logger.error(f"Error Image not found: {filename}")
            return jsonify({'error': 'Image not found'}), 404

    except Exception as e:
        logger.error(f"Error confirming detection: {e}")
        return jsonify({'error': 'Error confirming detection'}), 500
    finally:
        cursor.close()
        Database.return_connection(conn)
