from utils.logger import logger
from config import *
from flask_sock import Sock
from flask import Flask
from routes.upload_frame import upload_frame_bp
from routes.login import login_bp
from routes.logout import logout_bp
from routes.pothole_coordinates import pothole_coordinates_bp
from routes.pothole import pothole_bp
from routes.get_detected_image import get_detected_image_bp
from routes.registration import registration_bp
from routes.confirm import confirm_bp
from routes.get_detection_confirmation import get_detection_confirmation_bp
from flask_jwt_extended import JWTManager
#from hypercorn.middleware import AsyncioWSGIMiddleware

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ALGORITHM'] = JWT_ALGORITHM
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(upload_frame_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(pothole_coordinates_bp)
app.register_blueprint(pothole_bp)
app.register_blueprint(get_detected_image_bp)
app.register_blueprint(registration_bp)
app.register_blueprint(confirm_bp)
app.register_blueprint(get_detection_confirmation_bp)

#from gevent import pywsgi, spawn

# Deployment:
"""
# Wrap Flask app in AsyncioWSGIMiddleware for ASGI compatibility
asgi_app = AsyncioWSGIMiddleware(app)  # Define at module level for Uvicorn
"""

if __name__ == '__main__':
    # Debug mode
    app.run(host=SERVER_IP, port=SERVER_PORT)

    # Deployment
    """
    import uvicorn
    uvicorn.run("server:asgi_app", host=SERVER_IP, port=SERVER_PORT, workers=2)
    """
