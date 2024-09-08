import os
import time
from db.db_connection import Database
from services.image_service import ImageService

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

        # Simulate the detection confirmation process
        if DetectionService.send_detection_confirmation(filename, detection_name):
            DetectionService.confirm_detection(image_id, filename)
        else:
            DetectionService.delete_image_and_record(image_id, filename)

        cursor.close()
        conn.close()

    @staticmethod
    def send_detection_confirmation(filename, detection_name):
        # In a real-world scenario, you'd send a confirmation request to a client via WebSocket.
        # Here we'll simulate the confirmation process.

        print(f"Waiting for user confirmation for {filename} (Detection: {detection_name})")

        # Simulate a user response (for example, user confirms or rejects detection)
        # You could replace this with actual WebSocket logic in a real-world scenario.
        # For now, we'll simulate the user confirming the detection after a short delay.
        time.sleep(2)  # Simulate waiting for user confirmation
        confirmed = True  # Simulate that the user confirmed the detection
        return confirmed

    @staticmethod
    def confirm_detection(image_id, filename):
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
