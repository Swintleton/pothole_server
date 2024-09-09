from threading import Lock

# WebSocket state
clients = {}
pending_confirmations = {}
confirmation_lock = Lock()