import unittest
import sys
import os
from flask_jwt_extended import create_access_token
from datetime import timedelta

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import app

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        self.client = app.test_client()  # Initialize the test client

    def tearDown(self):
        pass  # Add any necessary cleanup logic here

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def get_valid_token(self, user_id=1):
        """
        Generate a valid token for testing.
        """
        with self.app.app_context():
            return create_access_token(identity=user_id)

    def get_expired_token(self, user_id=1):
        """
        Generate an expired token for testing.
        """
        with self.app.app_context():
            # Create an access token with a negative expiration time to ensure it is expired
            return create_access_token(identity=user_id, expires_delta=timedelta(seconds=-1))
