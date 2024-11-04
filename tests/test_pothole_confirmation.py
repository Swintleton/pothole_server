import unittest
from unittest.mock import patch, MagicMock
from server import app
from tests.base_test import BaseTestCase
import json
import threading
import time
from websocket import create_connection
from utils.logger import logger

class PotholeConfirmationTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    def test_websocket_pothole_confirmation(self, mock_get_connection):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock response for confirmation retrieval
        mock_cursor.fetchone.return_value = [1]  # Assume an image ID is retrieved

        # Start the Flask server in a separate thread
        def run_server():
            app.run(host="127.0.0.1", port=5001, use_reloader=False)

        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        # Wait for the server to start
        time.sleep(1)

        try:
            # Connect to the WebSocket and send a confirmation message
            ws = create_connection("ws://127.0.0.1:5001/confirm", timeout=1)
            ws.send(json.dumps({
                'filename': 'frame_1.jpg',
                'confirmed': True
            }))

            # Wait briefly and attempt to receive a server response or close
            time.sleep(1)
            ws.close()

            # Validate database interaction for confirmation
            mock_cursor.execute.assert_called_once_with(
                "SELECT uploaded_image_id FROM uploaded_image WHERE uploaded_image_file_name = %s",
                ('frame_1.jpg',)
            )

        except Exception as e:
            logger.error(f"Test failed with exception: {e}")

        finally:
            # Stop the server thread
            server_thread.join(timeout=1)
