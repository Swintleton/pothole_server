from utils.logger import logger
import os
import time
import json
from db.db_connection import Database
from services.image_service import ImageService
from services.websocket_service import send_detection_confirmation  # Updated import
from services.websocket_state import confirmation_lock, pending_confirmations  # Import WebSocket state
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

class DetectionService:
    @staticmethod
    def process_detection(image_id, filename, detection_id, auth_token, jwt_secret_key, jwt_algorithm):
        conn = Database.get_connection()
        if not conn:
            logger.error("Database connection failed.")
            return

        cursor = conn.cursor()

        # Retrieve the detection name based on detection_id
        cursor.execute("SELECT detection_name FROM detection WHERE detection_id = %s", (detection_id,))
        detection_name_result = cursor.fetchone()
        detection_name = detection_name_result[0] if detection_name_result else "Unknown Detection"

        cursor.close()

        # Check if the token exists and is valid
        if not auth_token or auth_token.strip() == '':
            logger.error(f"No valid auth token for image {filename}. Skipping confirmation.")
            DetectionService.delete_image_and_record(image_id, filename)
        else:
            # If token is present, proceed with confirmation
            if not DetectionService.send_detection_confirmation(filename, detection_name, auth_token, jwt_secret_key, jwt_algorithm):
                logger.info(f"Skipping confirmation for {filename}, deleting the image and its record.")
                DetectionService.delete_image_and_record(image_id, filename)

        Database.return_connection(conn)

    @staticmethod
    def send_detection_confirmation(filename, detection_name, auth_token, jwt_secret_key, jwt_algorithm):
        """
        Send a WebSocket confirmation request to the client.
        The confirmation is handled by the WebSocket connection.
        """
        logger.info(f"Waiting for user confirmation for {filename} (Detection: {detection_name})")

         # Remove "Bearer " prefix from the token if present
        if auth_token.startswith("Bearer "):
            auth_token = auth_token.split(" ")[1]

        # Verify the JWT token manually
        try:
            # Manually decode the token using PyJWT
            decoded_token = jwt.decode(auth_token, jwt_secret_key, algorithms=[jwt_algorithm])
            logger.info(f"Token verified for user {decoded_token['sub']}")  # Log user ID

            # Proceed with WebSocket confirmation
            with confirmation_lock:
                pending_confirmations[filename] = None

            send_detection_confirmation(filename, detection_name, auth_token, jwt_secret_key, jwt_algorithm)

            # Wait for the confirmation or timeout
            timeout_seconds = 8
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
                    logger.info(f"Timeout waiting for confirmation of {filename}")
                    return False

                time.sleep(1)
        except ExpiredSignatureError:
            logger.error("Token expired. Skipping confirmation and deleting image.")
            return False
        except InvalidTokenError as e:
            logger.error(f"Invalid token: {e}. Skipping confirmation and deleting image.")
            return False

    @staticmethod
    def confirm_detection(image_id, filename):
        """
        Mark the image as confirmed and move it to the confirmed folder.
        """
        conn = Database.get_connection()
        if conn:
            cursor = conn.cursor()

            # Update the image status to confirmed (status_id = 3)
            cursor.execute("""
                UPDATE uploaded_image 
                SET uploaded_image_status_id = 3, uploaded_image_modified_datetime = NOW() 
                WHERE uploaded_image_id = %s
            """, (image_id,))
            conn.commit()

            # Move the image to the confirmed folder
            file_path = os.path.join(ImageService.UPLOAD_FOLDER, filename)
            confirmed_path = os.path.join(ImageService.CONFIRMED_FOLDER, filename)

            if os.path.exists(file_path):
                os.rename(file_path, confirmed_path)

            cursor.close()
            Database.return_connection(conn)
            logger.info(f"Image {filename} confirmed and moved to confirmed folder.")

    @staticmethod
    def delete_image_and_record(image_id, filename):
        """
        Delete the image and its associated database record if detection is rejected.
        """
        try:
            conn = Database.get_connection()
            if conn:
                cursor = conn.cursor()

                # Delete the record from the database
                cursor.execute("DELETE FROM uploaded_image WHERE uploaded_image_id = %s", (image_id,))
                conn.commit()

                # Delete the image file
                file_path = os.path.join(ImageService.UPLOAD_FOLDER, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Delete the detected image file
                # Get base filename and extension
                base_filename, file_extension = os.path.splitext(filename)
                # Create the new filename with "_detected" added
                detected_filename = base_filename + "_detected" + file_extension

                # Create the full path with the modified filename
                file_path = os.path.join(ImageService.UPLOAD_FOLDER, detected_filename)

                # Check if the file exists and remove it
                if os.path.exists(file_path):
                    os.remove(file_path)

                cursor.close()
                Database.return_connection(conn)
                logger.info(f"Image {filename} and its record have been deleted.")

        except Exception as e:
            logger.error(f"Error deleting image and record: {e}")
