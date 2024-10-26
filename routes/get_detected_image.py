from flask import Blueprint, send_from_directory

get_detected_image_bp = Blueprint('get_detected_image', __name__)

@get_detected_image_bp.route('/confirmed/<filename>', methods=['GET'])
def get_detected_image(filename):
    return send_from_directory('uploaded_frames/confirmed', filename)
