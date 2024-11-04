from tests.base_test import BaseTestCase
from unittest.mock import patch, MagicMock
import threading

class AddPotholeTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    def test_add_pothole_authorized(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)  # Simulate user ID from token

        token = self.get_valid_token()

        response = self.client.post('/add_pothole', json={
            'latitude': 47.494367,
            'longitude': 19.060115
        }, headers={'Authorization': f'Bearer {token}'})

        self.assertEqual(response.status_code, 200)

    def test_add_pothole_unauthorized(self):
        response = self.client.post('/add_pothole', json={
            'latitude': 47.494367,
            'longitude': 19.060115
        })
        self.assertEqual(response.status_code, 401)

    def test_add_pothole_invalid_coordinates(self):
        token = self.get_valid_token()
        
        # Missing longitude
        response = self.client.post('/add_pothole', json={'latitude': 47.494367}, headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid coordinates', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_add_pothole_boundary_lat_long(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        
        token = self.get_valid_token()
        boundary_values = [
            {"latitude": 90, "longitude": 180},
            {"latitude": -90, "longitude": -180},
            {"latitude": 0, "longitude": 0},
            {"latitude": 80.58, "longitude": 170.97},
            {"latitude": 90, "longitude": 170.97},
            {"latitude": 80.58, "longitude": 180}
        ]

        for coordinates in boundary_values:
            response = self.client.post('/add_pothole', json=coordinates, headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)

    def test_add_pothole_invalid_lat_long(self):
        token = self.get_valid_token()
        invalid_coordinates = [
            {"latitude": "invalid", "longitude": "invalid"},
            {"latitude": 200, "longitude": 300},  # Out of bounds
            {"latitude": None, "longitude": None}
        ]

        for coordinates in invalid_coordinates:
            response = self.client.post('/add_pothole', json=coordinates, headers={'Authorization': f'Bearer {token}'})
            print(response.json)
            self.assertEqual(response.status_code, 400)

class EditPotholeTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    def test_edit_pothole_valid_data(self, mock_get_connection):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock the response for user role and ID check
        mock_cursor.fetchone.return_value = (1, 'Admin')  # Adjust as needed

        token = self.get_valid_token()

        # Send the request to edit a pothole with the necessary permissions
        response = self.client.put('/edit_pothole/1', json={
            'latitude': 47.494367,
            'longitude': 19.060115
        }, headers={'Authorization': f'Bearer {token}'})

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

    def test_edit_pothole_unauthorized(self):
        response = self.client.put('/edit_pothole/1', json={
            'latitude': 47.494367,
            'longitude': 19.060115
        })
        self.assertEqual(response.status_code, 401)
    
    @patch('db.db_connection.Database.get_connection')
    def test_edit_pothole_missing_coordinates(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        token = self.get_valid_token()

        response = self.client.put('/edit_pothole/1', json={}, headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid coordinates', response.json['error'])

class DeletePotholeTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    def test_delete_pothole_admin(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'Admin')  # Simulate admin role

        token = self.get_valid_token()

        response = self.client.delete('/delete_pothole/1', headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEqual(response.status_code, 200)

    def test_delete_pothole_unauthorized(self):
        response = self.client.delete('/delete_pothole/1')
        self.assertEqual(response.status_code, 401)
    
    @patch('db.db_connection.Database.get_connection')
    def test_delete_nonexistent_pothole(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate no pothole found

        token = self.get_valid_token()

        response = self.client.delete('/delete_pothole/999', headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEqual(response.status_code, 404)
        self.assertIn('Pothole not found', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_delete_pothole_unauthorized_user(self, mock_get_connection):
        # Mock database connection and cursor setup
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock response to simulate:
        # - Pothole creator has user_id = 2
        # - Logged-in user has user_id = 3 and role 'User' (neither the creator nor an admin)
        mock_cursor.fetchone.side_effect = [(2,), ('User',)]  # 1st for pothole, 2nd for role
        
        # Generate a token for a user who does not own the pothole
        token = self.get_valid_token(user_id=3)  # user_id 3 is not the creator or an admin
        
        response = self.client.delete('/delete_pothole/1', headers={'Authorization': f'Bearer {token}'})
        
        # Assert the response is a 403 Forbidden for unauthorized delete attempt
        self.assertEqual(response.status_code, 403)

    @patch('db.db_connection.Database.get_connection')
    def test_delete_pothole_nonexistent(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Pothole does not exist
        
        token = self.get_valid_token()
        
        response = self.client.delete('/delete_pothole/9999999', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 404)  # Expecting 404 Not Found

    #Concurrency Test with Multiple Pothole Additions
    @patch('db.db_connection.Database.get_connection')
    def test_concurrent_pothole_additions(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        
        token = self.get_valid_token()

        def add_pothole():
            response = self.client.post('/add_pothole', json={
                'latitude': 47.494367,
                'longitude': 19.060115
            }, headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)

        threads = [threading.Thread(target=add_pothole) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    @patch('db.db_connection.Database.get_connection')
    def test_delete_pothole_invalid_role(self, mock_get_connection):
        # Mock database connection and cursor setup
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simulate pothole creator has user_id=2 and logged-in user has an invalid role_id
        mock_cursor.fetchone.side_effect = [(2,), ('InvalidRole',)]  # 1st for pothole, 2nd for role
        
        # Generate token for a user with a non-creator, invalid role ID
        token = self.get_valid_token(user_id=3)  # user_id 3, not the creator, invalid role
        
        response = self.client.delete('/delete_pothole/1', headers={'Authorization': f'Bearer {token}'})
        
        # Assert the response is 403 Forbidden due to unauthorized attempt
        self.assertEqual(response.status_code, 403)
        self.assertIn('Unauthorized', response.json['error'])
