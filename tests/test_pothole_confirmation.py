import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
from server import app
from tests.base_test import BaseTestCase
import os
import json
import re

class ConfirmPotholeDetectionTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    @patch('os.rename')  # Mock file move to avoid existing file errors
    @patch('os.path.exists', return_value=True)
    def test_confirm_detection(self, mock_exists, mock_rename, mock_get_connection):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock database responses
        mock_cursor.fetchone.side_effect = [
            [1, 'frame_1.jpg'],  # Detection pending confirmation
            (1,),  # Image found for confirmation step
            None  # No further results after confirmation
        ]

        token = self.get_valid_token()
        user_id = 1  # Example user_id extracted from token
        threshold_time = datetime.now() - timedelta(seconds=30)

        with app.test_client() as client:
            # Step 1: Fetch pending detection
            response = client.get(
                '/get_detection_confirmation',
                headers={'Authorization': f'Bearer {token}'}
            )
            self.assertEqual(response.status_code, 200)
            detection_data = response.get_json()
            self.assertEqual(detection_data['filename'], 'frame_1_detected.jpg')

            # Step 2: Confirm the detection
            confirm_response = client.post(
                '/confirm',
                headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                data=json.dumps({
                    'filename': 'frame_1.jpg',
                    'confirmed': True
                })
            )
            self.assertEqual(confirm_response.status_code, 200)

            # Verify file rename (move) was called to avoid "file exists" error
            mock_rename.assert_called_once_with(
                os.path.join('uploaded_frames', 'frame_1.jpg'),
                os.path.join('uploaded_frames/confirmed', 'frame_1.jpg')
            )

            # Function to normalize SQL queries by removing whitespace
            def normalize_sql(query):
                return re.sub(r'\s+', ' ', query).strip()

            # Capture specific SQL queries for readability
            select_pending_detections = normalize_sql(mock_cursor.execute.call_args_list[0][0][0])
            select_for_confirmation = normalize_sql(mock_cursor.execute.call_args_list[1][0][0])
            update_confirmation_query = normalize_sql(mock_cursor.execute.call_args_list[3][0][0])

            # Verify the specific parts of SQL queries were executed
            self.assertIn("SELECT uploaded_image_id, uploaded_image_file_name", select_pending_detections)
            self.assertIn("WHERE uploaded_image_status_id = 2 AND uploaded_image_modified_datetime < %s", select_pending_detections)

            self.assertIn("SELECT uploaded_image_id, uploaded_image_file_name", select_for_confirmation)
            self.assertIn("WHERE uploaded_image_status_id = 2 AND uploaded_image_user_id = %s", select_for_confirmation)

            self.assertIn("UPDATE uploaded_image SET uploaded_image_status_id = 3", update_confirmation_query)

    @patch('db.db_connection.Database.get_connection')
    def test_confirm_detection_missing_auth_header(self, mock_get_connection):
        # Test for missing Authorization header
        with app.test_client() as client:
            response = client.post(
                '/confirm',
                headers={'Content-Type': 'application/json'},
                data=json.dumps({'filename': 'frame_1.jpg', 'confirmed': True})
            )
            self.assertEqual(response.status_code, 401)
            error_message = response.get_json().get("error")
            self.assertIn("Unauthorized", error_message)

    @patch('db.db_connection.Database.get_connection')
    def test_confirm_detection_invalid_auth_token(self, mock_get_connection):
        # Test for invalid Authorization token
        with app.test_client() as client:
            response = client.post(
                '/confirm',
                headers={'Authorization': 'Bearer invalid_token', 'Content-Type': 'application/json'},
                data=json.dumps({'filename': 'frame_1.jpg', 'confirmed': True})
            )
            self.assertEqual(response.status_code, 401)
            error_message = response.get_json().get("error")
            self.assertIn("Unauthorized", error_message)
