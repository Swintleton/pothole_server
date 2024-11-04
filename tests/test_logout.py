from tests.base_test import BaseTestCase
from unittest.mock import patch, MagicMock

class LogoutTestCase(BaseTestCase):
    def test_logout_success(self):
        token = self.get_valid_token()

        response = self.client.post('/logout', headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Logout successful"})

    def test_logout_no_auth(self):
        response = self.client.post('/logout')
        self.assertEqual(response.status_code, 401)

    def test_logout_invalid_token(self):
        # Simulate invalid token format
        response = self.client.post('/logout', headers={'Authorization': 'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token', response.json['error'])

    def test_logout_missing_bearer_prefix(self):
        # Simulate token without "Bearer " prefix
        token = self.get_valid_token()
        response = self.client.post('/logout', headers={'Authorization': token})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Logout failed', response.json['message'])

    def test_logout_expired_token(self):
        expired_token = self.get_expired_token()
        response = self.client.post('/logout', headers={
            'Authorization': f'Bearer {expired_token}'
        })
        # Expecting a 401 Unauthorized due to the expired token
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid token", response.json["error"])
