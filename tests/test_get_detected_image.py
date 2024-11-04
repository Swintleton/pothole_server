from tests.base_test import BaseTestCase
from unittest.mock import patch, MagicMock

class GetDetectedImageTestCase(BaseTestCase):
    def test_get_detected_image_invalid_token(self):
        response = self.client.get('/confirmed/frame_1.jpg', headers={
            'Authorization': 'Bearer invalid_token'
        })

        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_get_detected_image_missing_auth(self, mock_get_connection):
        # Simulate no auth header
        response = self.client.get('/confirmed/image_1_detected.jpg')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_get_detected_image_invalid_auth_format(self, mock_get_connection):
        # Simulate incorrect auth header format
        response = self.client.get('/confirmed/image_1_detected.jpg', headers={'Authorization': 'Token 12345'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_get_non_existent_image(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate no file found

        token = self.get_valid_token()
        response = self.client.get('/confirmed/non_existent.jpg', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('File not found', response.json['error'])
