from flask import Flask
from sockets.confirmation_socket import sock
from routes.upload_frame import upload_frame_bp
from routes.login import login_bp
from routes.logout import logout_bp
from routes.pothole_coordinates import pothole_coordinates_bp
from monitoring import monitor_and_confirm_detections
import threading

app = Flask(__name__)

# Register blueprints and websockets
app.register_blueprint(upload_frame_bp)
app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(pothole_coordinates_bp)
sock.init_app(app)

if __name__ == '__main__':
    monitoring_thread = threading.Thread(target=monitor_and_confirm_detections, daemon=True)
    monitoring_thread.start()
    app.run(host='192.168.0.115', port=5000)
