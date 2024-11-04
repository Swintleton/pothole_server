from utils.logger import logger
from flask import Blueprint, send_from_directory, request, jsonify
from utils.auth import Auth
import os

get_detected_image_bp = Blueprint('get_detected_image', __name__)

@get_detected_image_bp.route('/confirmed/<filename>', methods=['GET'])
def get_detected_image(filename):
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

    # Verify the requested file exists
    file_path = os.path.join('uploaded_frames', 'confirmed', filename)
    if not os.path.exists(file_path):
        logger.error(f"File {filename} not found in confirmed directory")
        return jsonify({'error': 'File not found'}), 404

    return send_from_directory('uploaded_frames/confirmed', filename)
