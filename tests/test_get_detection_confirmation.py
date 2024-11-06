import unittest
from unittest.mock import patch, MagicMock
from server import app
from tests.base_test import BaseTestCase

class GetPotholeConfirmationTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    @patch('os.path.exists', return_value=True)
    def test_get_detection_confirmation(self, mock_exists, mock_get_connection):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Define mock responses for database fetches
        mock_cursor.fetchone.side_effect = [
            [1, 'frame_1.jpg'],  # Pending detection
            None  # No further detections
        ]

        token = self.get_valid_token()
        user_id = 1  # Example user_id extracted from token

        with app.test_client() as client:
            # Step 1: Fetch pending detection (image waiting for confirmation)
            response = client.get(
                '/get_detection_confirmation',
                headers={'Authorization': f'Bearer {token}'}
            )

            # Assert response status and retrieved data
            self.assertEqual(response.status_code, 200)
            detection_data = response.get_json()
            self.assertEqual(detection_data['filename'], 'frame_1_detected.jpg')

            # Retrieve and label the specific SQL query executed
            query_select_pending_detection = mock_cursor.execute.call_args_list[1][0][0]
            query_select_params = mock_cursor.execute.call_args_list[1][0][1]

            # Assertions on SQL query contents and parameters
            self.assertIn("SELECT uploaded_image_id, uploaded_image_file_name", query_select_pending_detection)
            self.assertIn("WHERE uploaded_image_status_id = 2 AND uploaded_image_user_id = %s", query_select_pending_detection)
            self.assertEqual(query_select_params, (user_id,))

    @patch('db.db_connection.Database.get_connection')
    def test_get_detection_confirmation_missing_auth_header(self, mock_get_connection):
        # Test for missing Authorization header
        with app.test_client() as client:
            response = client.get('/get_detection_confirmation')
            self.assertEqual(response.status_code, 401)
            error_message = response.get_json().get("error")
            self.assertIn("Unauthorized", error_message)

    @patch('db.db_connection.Database.get_connection')
    def test_get_detection_confirmation_invalid_auth_token(self, mock_get_connection):
        # Test for invalid Authorization token
        with app.test_client() as client:
            response = client.get(
                '/get_detection_confirmation',
                headers={'Authorization': 'Bearer invalid_token'}
            )
            self.assertEqual(response.status_code, 401)
            error_message = response.get_json().get("error")
            self.assertIn("Unauthorized", error_message)
