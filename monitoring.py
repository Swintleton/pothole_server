import time
from db.db_connection import Database
from services.detection_service import DetectionService

def monitor_and_confirm_detections():
    """
    This function continuously monitors the database for images
    with a status of "DETECTED" (status_id = 2) and processes them for confirmation.
    """
    while True:
        try:
            # Establish a connection to the database
            conn = Database.get_connection()
            if not conn:
                print("Database connection failed. Retrying in 5 seconds...")
                time.sleep(5)
                continue
            
            cursor = conn.cursor()

            # Fetch images with status "DETECTED" (status_id = 2)
            cursor.execute("""
                SELECT uploaded_image_id, uploaded_image_file_name, uploaded_image_detection_id
                FROM uploaded_image 
                WHERE uploaded_image_status_id = 2
            """)
            detections = cursor.fetchall()

            # Process each detection
            for detection in detections:
                image_id, filename, detection_id = detection
                print(f"Processing detection for image {filename} (ID: {image_id})")
                
                # Use the refactored DetectionService to process the detection
                DetectionService.process_detection(image_id, filename, detection_id)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error in monitoring detections: {e}")
        finally:
            # Wait for 3 seconds before the next iteration
            time.sleep(3)
