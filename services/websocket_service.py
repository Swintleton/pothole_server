import json
from services.websocket_state import clients, confirmation_lock, pending_confirmations

def send_detection_confirmation(filename, detection_name):
    """
    Send a detection confirmation request to all connected WebSocket clients.
    """
    print(f"Sending WebSocket message to clients: {filename} ({detection_name})")

    # Lock for thread safety
    with confirmation_lock:
        pending_confirmations[filename] = None

    ws_message = json.dumps({
        'type': 'confirmation_request',
        'filename': filename,
        'detection_name': detection_name
    })

    for client_id, ws in list(clients.items()):
        try:
            ws.send(ws_message)
        except Exception as e:
            print(f"Failed to send to client {client_id}: {e}")
            del clients[client_id]
