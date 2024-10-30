from utils.logger import logger
from flask_sock import Sock
from flask import Flask
from routes.upload_frame import upload_frame_bp
from routes.login import login_bp
from routes.logout import logout_bp
from routes.pothole_coordinates import pothole_coordinates_bp
from routes.pothole import pothole_bp
from routes.get_detected_image import get_detected_image_bp
from routes.registration import registration_bp
from monitoring import monitor_and_confirm_detections
import threading
from flask_jwt_extended import JWTManager

# Import sock from websocket.py
from services.websocket import sock

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'pothole'
app.config['JWT_ALGORITHM'] = 'HS256'
jwt = JWTManager(app)

# Register blueprints and websockets
app.register_blueprint(upload_frame_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(pothole_coordinates_bp)
app.register_blueprint(pothole_bp)
app.register_blueprint(get_detected_image_bp)
app.register_blueprint(registration_bp)

# Initialize Sock for WebSocket support by linking it to the app
sock.init_app(app)

# Import WebSocket handlers
import sockets.confirmation_socket

#from gevent import pywsgi
#from geventwebsocket.handler import WebSocketHandler

if __name__ == '__main__':
    monitoring_thread = threading.Thread(
        target=monitor_and_confirm_detections, 
        args=(app.config['JWT_SECRET_KEY'], app.config['JWT_ALGORITHM']), 
        daemon=True
    )
    monitoring_thread.start()

    # Start the server with WebSocket support using gevent
    app.run(host='192.168.0.115', port=5000)
    #server = pywsgi.WSGIServer(('192.168.0.115', 5000), app, handler_class=WebSocketHandler)
    #server.serve_forever()