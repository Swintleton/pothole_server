import sys
import os
from unittest.mock import patch, MagicMock
import bcrypt
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from base_test import BaseTestCase

class LoginTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    def test_login_success(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, bcrypt.hashpw(b'admin', bcrypt.gensalt()).decode('utf-8'), 'Admin')

        response = self.client.post('/login', json={
            'username': 'admin',
            'password': 'admin'
        })

        print(response.json)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Login successful', response.json['message'])

    def test_login_missing_fields(self):
        response = self.client.post('/login', json={
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Username and password are required', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_invalid_credentials(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate no user found

        response = self.client.post('/login', json={
            'username': 'wronguser',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 401)

    def test_login_excessively_long_credentials(self):
        long_username = 'user' * 1000
        long_password = 'pass' * 1000
        response = self.client.post('/login', json={
            'username': long_username,
            'password': long_password
        })
        self.assertEqual(response.status_code, 400)
    
    def test_login_with_special_characters_in_username(self):
        response = self.client.post('/login', json={
            'username': 'invalidspecial!@#$%^&*()_+=username',
            'password': 'Password@123'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid username format', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_multiple_concurrent_logins(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock a valid user login
        hashed_password = bcrypt.hashpw(b'concurrentUserPass', bcrypt.gensalt()).decode('utf-8')
        mock_cursor.fetchone.return_value = (1, hashed_password, 'User')

        def login_user():
            response = self.client.post('/login', json={
                'username': 'concurrentUser',
                'password': 'concurrentUserPass'
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn('Login successful', response.json['message'])

        # Execute concurrent logins
        threads = [threading.Thread(target=login_user) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
