import time
from db.db_connection import Database
from services.detection_service import DetectionService

def monitor_and_confirm_detections():
    while True:
        conn = Database.get_connection()
        if not conn:
            time.sleep(5)
            continue
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT uploaded_image_id, uploaded_image_file_name, uploaded_image_detection_id
            FROM uploaded_image WHERE uploaded_image_status_id = 2
        """)
        detections = cursor.fetchall()
        
        for detection in detections:
            image_id, filename, detection_id = detection
            DetectionService.process_detection(image_id, filename, detection_id)
        
        cursor.close()
        conn.close()
        time.sleep(3)
