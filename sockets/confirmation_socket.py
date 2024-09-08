import json
from threading import Lock
from flask_sock import Sock

sock = Sock()

clients = {}
pending_confirmations = {}
confirmation_lock = Lock()

@sock.route('/confirm')
def confirm(ws):
    client_id = id(ws)
    clients[client_id] = ws

    try:
        while True:
            message = ws.receive()
            if message:
                data = json.loads(message)
                filename = data.get('filename')
                confirmed = data.get('confirmed', False)

                handle_user_confirmation({'filename': filename, 'confirmed': confirmed})

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        del clients[client_id]

def handle_user_confirmation(data):
    filename = data.get('filename')
    confirmed = data.get('confirmed', False)
    with confirmation_lock:
        pending_confirmations[filename] = confirmed
