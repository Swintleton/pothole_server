from utils.logger import logger
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import json
from services.websocket_state import clients, confirmation_lock, pending_confirmations
import os

def send_detection_confirmation(filename, detection_name, auth_token, jwt_secret_key, jwt_algorithm):
    """
    Send a detection confirmation request to all connected WebSocket clients.
    If the token is expired or invalid, skip sending the confirmation request.
    """
    try:
        # Manually decode the token using the JWT secret and algorithm
        if auth_token.startswith("Bearer "):
            auth_token = auth_token.split(" ")[1]

        # Decode the token
        decoded_token = jwt.decode(auth_token, jwt_secret_key, algorithms=[jwt_algorithm])
        user_id = decoded_token['sub']  # Assuming 'sub' holds the user ID

        # Lock for thread safety
        with confirmation_lock:
            pending_confirmations[filename] = None

        filename_without_ext, ext = os.path.splitext(filename)
        detected_image_url = f"http://192.168.0.115:5000/confirmed/{filename_without_ext}_detected.jpg"

        ws_message = json.dumps({
            'type': 'confirmation_request',
            'filename': filename,
            'detection_name': detection_name,
            'image_url': detected_image_url  # Include the URL to the detected image
        })

        # Use the ws.send() method to broadcast the message to all connected clients
        for client_id, ws in list(clients.items()):
            try:
                ws.send(ws_message)  # Sending message via the WebSocket directly
                logger.info(f"Sending WebSocket message to client {client_id}: {filename} ({detection_name})")
            except Exception as e:
                logger.error(f"Failed to send to client {client_id}: {e}")
                del clients[client_id]

    except ExpiredSignatureError:
        logger.error("Token expired. Skipping confirmation.")
        return False
    except InvalidTokenError as e:
        logger.error(f"Invalid token: {e}. Skipping confirmation.")
        return False
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return False
