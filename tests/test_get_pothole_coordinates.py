from tests.base_test import BaseTestCase
from unittest.mock import patch, MagicMock

class GetPotholeCoordinatesTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    def test_get_pothole_coordinates_success(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 47.494367, 19.060115, 'pothole_1.jpg', 1)
        ]

        token = self.get_valid_token()

        response = self.client.get('/potholes', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['filename'], 'pothole_1_detected.jpg')

    @patch('db.db_connection.Database.get_connection')
    def test_get_pothole_coordinates_empty(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        token = self.get_valid_token()

        response = self.client.get('/potholes', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])
