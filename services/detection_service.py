import os
import time
import json
from db.db_connection import Database
from services.image_service import ImageService
from services.websocket_service import send_detection_confirmation  # Updated import
from services.websocket_state import confirmation_lock, pending_confirmations  # Import WebSocket state

class DetectionService:
    @staticmethod
    def process_detection(image_id, filename, detection_id):
        conn = Database.get_connection()
        if not conn:
            print("Database connection failed.")
            return

        cursor = conn.cursor()

        # Retrieve the detection name based on detection_id
        cursor.execute("SELECT detection_name FROM detection WHERE detection_id = %s", (detection_id,))
        detection_name_result = cursor.fetchone()
        detection_name = detection_name_result[0] if detection_name_result else "Unknown Detection"

        cursor.close()

        # Request user confirmation via WebSocket
        if DetectionService.send_detection_confirmation(filename, detection_name):
            DetectionService.confirm_detection(image_id, filename)
        else:
            DetectionService.delete_image_and_record(image_id, filename)

        conn.close()

    @staticmethod
    def send_detection_confirmation(filename, detection_name):
        """
        Send a WebSocket confirmation request to the client.
        The confirmation is handled by the WebSocket connection.
        """
        print(f"Waiting for user confirmation for {filename} (Detection: {detection_name})")

        # Send WebSocket message to the client
        with confirmation_lock:
            pending_confirmations[filename] = None

        send_detection_confirmation(filename, detection_name)

        # Wait for the confirmation or timeout
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
            conn.close()
            print(f"Image {filename} confirmed and moved to confirmed folder.")

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

                cursor.close()
                conn.close()
                print(f"Image {filename} and its record have been deleted.")

        except Exception as e:
            print(f"Error deleting image and record: {e}")
