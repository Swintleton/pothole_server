from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from PIL import Image, ExifTags
import subprocess
import re
import json
import bcrypt
import psycopg2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded_frames'
CONFIRMED_FOLDER = 'uploaded_frames/confirmed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONFIRMED_FOLDER, exist_ok=True)

YOLO_WEIGHTS = 'E:/yolov5_runs/exp8/weights/best.pt'  # Path to your YOLOv5 weights file

users = {
    "admin": "admin"  # A test username and password
}

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="123456"
    )
    return conn

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query the database for the user
    cursor.execute("SELECT user_password FROM \"user\" WHERE user_login = %s", (username,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        stored_password = result[0]

        # Verify the provided password with the stored hashed password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({"message": "Login successful", "auth_token": "fake_token"}), 200  # Replace with a real token
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    else:
        return jsonify({"error": "Invalid username or password"}), 401

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
        # cases: image don't have getexif
        pass

def preprocess_output(output):
    # Replace single quotes with double quotes and add double quotes around keys
    output = re.sub(r"(\w+):", r'"\1":', output)
    output = output.replace("'", '"')
    return output

@app.route('/upload_frame', methods=['POST'])
def upload_frame():
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
                img = img.resize((416, 416))  # Resize the image to 416x416
                img.save(file_path)

            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')

            if latitude and longitude:
                gps_data = f"{latitude},{longitude}"
                gps_file_path = file_path.replace('.jpg', '.txt')
                with open(gps_file_path, 'w') as gps_file:
                    gps_file.write(gps_data)
            else:
                print("No GPS data received")

            # Call YOLOv5 for pothole detection
            result = subprocess.run(['python', 'yolov5/detect.py', '--weights', YOLO_WEIGHTS, '--img', '416', '--conf', '0.65', '--source', file_path, '--device', 'cpu'], capture_output=True, text=True)
            print("--------------------------------------------")
            print(result.stdout)
            print("--------------------------------------------")
            print("\r\n")

            if result.stdout.strip():  # Check if the result is not an empty string
                try:
                    preprocessed_output = preprocess_output(result.stdout)
                    detection_results = json.loads(preprocessed_output)
                    if 'pothole' in detection_results.values():
                        return jsonify({'message': 'Pothole detected. Confirm?', 'filename': filename, 'latitude': latitude, 'longitude': longitude}), 200
                    else:
                        os.remove(file_path)  # Remove the frame if no pothole is detected
                        os.remove(file_path.replace('.jpg', '.txt'))  # Remove the GPS data file
                        return jsonify({'message': 'No pothole detected'}), 200
                except json.JSONDecodeError as json_error:
                    print(f"JSONDecodeError: {json_error}")
                    os.remove(file_path)  # Remove the frame if JSON decoding fails
                    os.remove(file_path.replace('.jpg', '.txt'))  # Remove the GPS data file
                    return jsonify({'message': 'No pothole detected'}), 200
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    return jsonify({'error': str(e)}), 500
            else:
                os.remove(file_path)  # Remove the frame if result is empty
                os.remove(file_path.replace('.jpg', '.txt'))  # Remove the GPS data file
                return jsonify({'message': 'No pothole detected'}), 200

        except Exception as e:
            print(f"Exception while processing the image: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/confirm_detection', methods=['POST'])
def confirm_detection():
    data = request.get_json()
    filename = data.get('filename')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    confirmed = data.get('confirmed', False)

    if filename and latitude and longitude:
        gps_file_path = os.path.join(UPLOAD_FOLDER, filename.replace('.jpg', '.txt'))
        if confirmed:
            # Move only the GPS data file to the confirmed folder
            os.rename(gps_file_path, os.path.join(CONFIRMED_FOLDER, filename.replace('.jpg', '.txt')))
            
            # Remove the frame
            frame_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(frame_path):
                os.remove(frame_path)
            
            return jsonify({'message': 'Detection confirmed and saved'}), 200
        else:
            # Remove the frame and GPS data if not confirmed
            frame_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(frame_path):
                os.remove(frame_path)
            if os.path.exists(gps_file_path):
                os.remove(gps_file_path)
            confirmed_frame_path = os.path.join(CONFIRMED_FOLDER, filename)
            if os.path.exists(confirmed_frame_path):
                os.remove(confirmed_frame_path)
            return jsonify({'message': 'Detection not confirmed, files deleted'}), 200
    else:
        frame_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(frame_path):
            os.remove(frame_path)
        if os.path.exists(gps_file_path):
            os.remove(gps_file_path)
        confirmed_frame_path = os.path.join(CONFIRMED_FOLDER, filename)
        if os.path.exists(confirmed_frame_path):
            os.remove(confirmed_frame_path)
        return jsonify({'error': 'Invalid data'}), 400

if __name__ == '__main__':
    app.run(host='192.168.0.115', port=5000)
