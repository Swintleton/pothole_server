from utils.logger import logger
from services.websocket_state import clients, confirmation_lock, pending_confirmations
from db.db_connection import Database
from services.detection_service import DetectionService
import json
from services.websocket import sock

# WebSocket endpoint for handling confirmation
@sock.route('/confirm')
def confirm(ws):
    client_id = id(ws)
    clients[client_id] = ws
    logger.info(f"Client {client_id} connected via WebSocket")

    try:
        while True:
            message = ws.receive()
            if message:
                data = json.loads(message)
                filename = data.get('filename')
                confirmed = data.get('confirmed', False)

                # Handle confirmation response from the client
                handle_user_confirmation({'filename': filename, 'confirmed': confirmed})
                logger.info(f"Received message: {message}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"Client {client_id} disconnected")
        del clients[client_id]

def handle_user_confirmation(data):
    """
    Handle user confirmation when received via WebSocket.
    """
    filename = data.get('filename')
    confirmed = data.get('confirmed', False)

    with confirmation_lock:
        if filename in pending_confirmations:
            pending_confirmations[filename] = confirmed
            if confirmed:
                logger.info(f"User confirmed detection for {filename}")
                conn = Database.get_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT uploaded_image_id FROM uploaded_image WHERE uploaded_image_file_name = %s
                    """, (filename,))
                    result = cursor.fetchone()

                    if result:
                        image_id = result[0]
                        DetectionService.confirm_detection(image_id, filename)

                    cursor.close()
                    Database.return_connection(conn)
            else:
                logger.info(f"User did not confirm detection for {filename}")
