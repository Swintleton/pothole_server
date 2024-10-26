from utils.logger import logger
import time
from db.db_connection import Database
from services.detection_service import DetectionService

def monitor_and_confirm_detections(jwt_secret_key, jwt_algorithm):
    """
    This function continuously monitors the database for images
    with a status of "DETECTED" (status_id = 2) and processes them for confirmation.
    """
    while True:
        try:
            # Establish a connection to the database
            conn = Database.get_connection()
            if not conn:
                logger.info("Database connection failed. Retrying in 5 seconds...")
                time.sleep(5)
                continue
            
            cursor = conn.cursor()

            # Fetch images with status "DETECTED" (status_id = 2)
            cursor.execute("""
                SELECT uploaded_image_id, uploaded_image_file_name, uploaded_image_detection_id, user_auth_token
                FROM uploaded_image
                INNER JOIN "user" ON user_id = uploaded_image_user_id
                WHERE uploaded_image_status_id = 2
            """)
            detections = cursor.fetchall()

            # Process each detection
            for detection in detections:
                image_id, filename, detection_id, auth_token = detection
                logger.info(f"Processing detection for image {filename} (ID: {image_id})")
                
                # Use the refactored DetectionService to process the detection
                DetectionService.process_detection(image_id, filename, detection_id, auth_token, jwt_secret_key, jwt_algorithm)

            cursor.close()
            Database.return_connection(conn)

        except Exception as e:
            logger.error(f"Error in monitoring detections: {e}")
        finally:
            # Wait for 3 seconds before the next iteration
            time.sleep(3)
