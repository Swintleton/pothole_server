import unittest
from unittest.mock import patch, MagicMock
from flask import jsonify
from db.db_connection import Database
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import app

class RegistrationTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('db.db_connection.Database.get_connection')  # Mock database connection
    def test_register_user_successful(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate no existing user

        # Simulate successful insert
        mock_cursor.execute.return_value = True

        response = self.client.post('/register', json={
            'username': 'testuser',
            'login': 'testlogin',
            'password': 'Test@1234',
            'email': 'testuser@example.com',
            'phone': '+123456789'
        })

        print(response.json)

        self.assertEqual(response.status_code, 201)
        self.assertIn('Registration successful', response.json['message'])

    def test_register_user_missing_fields(self):
        response = self.client.post('/register', json={
            'username': '',
            'login': '',
            'password': '',
            'email': 'invalid'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('required', response.json['error'])

    def test_register_user_invalid_email(self):
        response = self.client.post('/register', json={
            'username': 'user1',
            'login': 'user1login',
            'password': 'Password@123',
            'email': 'invalid-email-format'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid email format', response.json['error'])

    def test_register_user_password_strength(self):
        response = self.client.post('/register', json={
            'username': 'user2',
            'login': 'user2login',
            'password': 'weakpassword',
            'email': 'user2@example.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Password must be at least 8 characters', response.json['error'])
    
    def test_register_weak_password_missing_number(self):
        response = self.client.post('/register', json={
            'username': 'user2',
            'login': 'user2login',
            'password': 'NoNumber!',
            'email': 'user2@example.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Password must be at least 8 characters', response.json['error'])

    def test_register_weak_password_missing_special_character(self):
        response = self.client.post('/register', json={
            'username': 'user3',
            'login': 'user3login',
            'password': 'Password123',
            'email': 'user3@example.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Password must be at least 8 characters', response.json['error'])
    
    @patch('db.db_connection.Database.get_connection')
    def test_register_duplicate_email(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Define side effects to simulate unique login and existing email
        def side_effect(query, params):
            if "user_login = %s" in query:
                return None  # Simulate unique login
            elif "user_email = %s" in query:
                return (1,)  # Simulate existing email

        # Apply side effect only to `fetchone` calls
        mock_cursor.fetchone.side_effect = [None, (1,)]  # First call returns None (unique login), second call returns existing email

        response = self.client.post('/register', json={
            'username': 'newuser',
            'login': 'newlogin',
            'password': 'Test@1234',
            'email': 'existing@example.com',  # Duplicate email
            'phone': '+123456789'
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('Email already exists', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_register_existing_user(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)  # Simulate existing user

        response = self.client.post('/register', json={
            'username': 'testuser',
            'login': 'existing_login',
            'password': 'Test@1234',
            'email': 'testuser@example.com',
            'phone': '+123456789'
        })

        self.assertEqual(response.status_code, 400)
    
    def test_register_empty_username(self):
        response = self.client.post('/register', json={
            'username': '',
            'login': 'user3login',
            'password': 'Password@123',
            'email': 'user3@example.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Username, login, password, and email are required', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_register_with_missing_data(self, mock_get_connection):
        incomplete_data = [
            {"username": "user1", "email": "user1@example.com"},
            {"login": "login1", "password": "Password@123"},
            {"email": "email@example.com", "password": "Password@123"},
        ]

        for data in incomplete_data:
            response = self.client.post('/register', json=data)
            self.assertEqual(response.status_code, 400)
            self.assertIn("required", response.json['error'])  # Should mention required fields
