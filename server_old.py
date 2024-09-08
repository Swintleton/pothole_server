from flask import Flask, request, jsonify, g
from werkzeug.utils import secure_filename
import os
from PIL import Image, ExifTags
import json
import bcrypt
import psycopg2
import time
from datetime import datetime, timedelta
from threading import Lock
import threading
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)
confirmation_lock = Lock()
pending_confirmations = {}
clients = {}  # Store active WebSocket clients

UPLOAD_FOLDER = 'uploaded_frames'
CONFIRMED_FOLDER = 'uploaded_frames/confirmed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONFIRMED_FOLDER, exist_ok=True)

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="pothole",
            user="postgres",
            password="123456"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Mock token authentication for simplicity
def verify_token(token):
    if token == "fake_token":
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM \"user\" WHERE user_login = 'admin'")
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user:
                g.user_id = user[0]
                return True
    return False

# Fix image orientation if necessary
def correct_image_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass

# Upload frame handler
@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    try:
        auth_token = request.headers.get('Authorization')
        if not auth_token or not verify_token(auth_token.split(" ")[1]):
            return jsonify({'error': 'Unauthorized'}), 401

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            try:
                with Image.open(file_path) as img:
                    correct_image_orientation(img)
                    img = img.resize((416, 416))
                    img.save(file_path)

                latitude = request.form.get('latitude')
                longitude = request.form.get('longitude')

                if latitude and longitude:
                    conn = get_db_connection()
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

            except Exception as e:
                print(f"Exception while processing the image: {e}")
                return jsonify({'error': str(e)}), 500

        return ('', 204)

    except Exception as e:
        print(f"Error uploading frame: {e}")
        return jsonify({'error': 'Error uploading frame'}), 500

# Monitor for detections and ask for user confirmation
def monitor_and_confirm_detections():
    while True:
        try:
            conn = get_db_connection()
            if not conn:
                print("Database connection failed.")
                time.sleep(5)
                continue
            cursor = conn.cursor()

            # Check for any images with DETECTED status
            cursor.execute("""
                SELECT uploaded_image_id, uploaded_image_file_name, uploaded_image_detection_id
                FROM uploaded_image 
                WHERE uploaded_image_status_id = 2
            """)
            detections = cursor.fetchall()

            if detections:
                for detection in detections:
                    image_id, filename, detection_id = detection
                    cursor.execute("SELECT detection_name FROM detection WHERE detection_id = %s", (detection_id,))
                    detection_name_result = cursor.fetchone()
                    detection_name = detection_name_result[0] if detection_name_result else "Unknown Detection"

                    # Notify the user about the detected pothole
                    if send_detection_confirmation(filename, detection_name):
                        confirm_detection(image_id, filename)
                    else:
                        delete_image_and_record(image_id, filename)
            else:
                print("No detections found. Waiting for 3 seconds.")
                time.sleep(3)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error in monitoring detections: {e}")
            time.sleep(5)

# Delete image and its database record
def delete_image_and_record(image_id, filename):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM uploaded_image WHERE uploaded_image_id = %s", (image_id,))
            conn.commit()

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                os.remove(file_path)

            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Error deleting image and record: {e}")

# Confirm detection and move the image to the confirmed folder
def confirm_detection(image_id, filename):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE uploaded_image 
                SET uploaded_image_status_id = 3, uploaded_image_modified_datetime = NOW() 
                WHERE uploaded_image_id = %s
            """, (image_id,))
            conn.commit()

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            confirmed_path = os.path.join(CONFIRMED_FOLDER, filename)

            if os.path.exists(file_path):
                os.rename(file_path, confirmed_path)

            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Error confirming detection: {e}")

@app.route('/')
def index():
    return "WebSocket server is running."

# WebSocket handler for confirmation
@sock.route('/confirm')
def confirm(ws):
    client_id = id(ws)
    clients[client_id] = ws

    print("Client connected via WebSocket")
    try:
        while True:
            message = ws.receive()
            if message:
                data = json.loads(message)
                filename = data.get('filename')
                confirmed = data.get('confirmed', False)

                if confirmed:
                    handle_user_confirmation({'filename': filename, 'confirmed': True})
                else:
                    handle_user_confirmation({'filename': filename, 'confirmed': False})
                
                print(f"Received message: {message}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("Client disconnected")
        del clients[client_id]

# Broadcast confirmation request via WebSocket
def send_detection_confirmation(filename, detection_name):
    with confirmation_lock:
        pending_confirmations[filename] = None

    ws_message = json.dumps({
        'type': 'confirmation_request',
        'filename': filename,
        'detection_name': detection_name
    })

    print(f"Waiting for user confirmation for {filename} (Detection: {detection_name})")

    for client_id, ws in list(clients.items()):
        try:
            ws.send(ws_message)
        except Exception as e:
            print(f"Failed to send to client {client_id}: {e}")
            del clients[client_id]

    timeout_seconds = 120
    start_time = time.time()

    while True:
        with confirmation_lock:
            user_response = pending_confirmations.get(filename)

        if user_response is not None:
            with confirmation_lock:
                del pending_confirmations[filename]
            return user_response

        if time.time() - start_time > timeout_seconds:
            with confirmation_lock:
                del pending_confirmations[filename]
            print(f"Timeout waiting for confirmation of {filename}")
            return False

        time.sleep(1)

def handle_user_confirmation(data):
    filename = data.get('filename')
    confirmed = data.get('confirmed', False)

    with confirmation_lock:
        if filename in pending_confirmations:
            pending_confirmations[filename] = confirmed
            if confirmed:
                print(f"User confirmed detection for {filename}")
            else:
                print(f"User did not confirm detection for {filename}")

if __name__ == '__main__':
    monitoring_thread = threading.Thread(target=monitor_and_confirm_detections, daemon=True)
    monitoring_thread.start()

    app.run(host='192.168.0.115', port=5000)
