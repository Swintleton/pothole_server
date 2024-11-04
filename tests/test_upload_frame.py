import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image
from flask import Flask
from server import app
from tests.base_test import BaseTestCase
import io

class UploadFrameTestCase(BaseTestCase):
    @patch('db.db_connection.Database.get_connection')
    def test_upload_frame_success(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        token = self.get_valid_token()

        # Generate a simple valid JPEG image in memory
        image_data = BytesIO()
        image = Image.new("RGB", (416, 416), color="red")
        image.save(image_data, format="JPEG")
        image_data.seek(0)  # Reset the buffer to the beginning

        data = {
            'file': (image_data, 'frame_1.jpg'),
            'latitude': '47.494367',
            'longitude': '19.060115'
        }

        response = self.client.post('/upload_frame', data=data, headers={
            'Authorization': f'Bearer {token}'
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)

    def test_upload_frame_no_auth(self):
        data = {
            'file': (io.BytesIO(b"fake image data"), 'frame_1.jpg'),
            'latitude': '47.494367',
            'longitude': '19.060115'
        }

        response = self.client.post('/upload_frame', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 401)

    def test_upload_frame_no_file(self):
        token = self.get_valid_token()
        response = self.client.post('/upload_frame', headers={
            'Authorization': f'Bearer {token}'
        })

        self.assertEqual(response.status_code, 400)

    @patch('db.db_connection.Database.get_connection')
    def test_upload_frame_invalid_file_type(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        token = self.get_valid_token()

        # Create a fake text file instead of an image
        data = {
            'file': (io.BytesIO(b"This is a text file, not an image"), 'not_image.txt'),
            'latitude': '47.494367',
            'longitude': '19.060115'
        }

        response = self.client.post('/upload_frame', data=data, headers={
            'Authorization': f'Bearer {token}'
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid image file type', response.json['error'])

    def test_upload_large_image(self):
        token = self.get_valid_token()
        # Generate a large image in memory
        image_data = BytesIO()
        image = Image.new("RGB", (5000, 5000), color="blue")
        image.save(image_data, format="JPEG")
        image_data.seek(0)

        data = {
            'file': (image_data, 'large_image.jpg'),
            'latitude': '47.494367',
            'longitude': '19.060115'
        }

        response = self.client.post('/upload_frame', data=data, headers={
            'Authorization': f'Bearer {token}'
        }, content_type='multipart/form-data')
        self.assertIn(response.status_code, [200, 413])  # 413 if too large

    def test_upload_frame_missing_location(self):
        token = self.get_valid_token()
        # Generate a simple image in memory
        image_data = BytesIO()
        image = Image.new("RGB", (416, 416), color="green")
        image.save(image_data, format="JPEG")
        image_data.seek(0)

        data = {
            'file': (image_data, 'no_location_image.jpg')
        }

        response = self.client.post('/upload_frame', data=data, headers={
            'Authorization': f'Bearer {token}'
        }, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid coordinates', response.json['error'])

    @patch('db.db_connection.Database.get_connection')
    def test_upload_frame_boundary_lat_long(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)  # Simulate a successful DB entry

        token = self.get_valid_token()

        # Boundary values for latitude and longitude
        boundary_values = [
            {"latitude": 90, "longitude": 180},
            {"latitude": -90, "longitude": -180},
            {"latitude": 0, "longitude": 0},
            {"latitude": 80.58, "longitude": 170.97},
            {"latitude": 90, "longitude": 170.97},
            {"latitude": 80.58, "longitude": 180}
        ]

        for coordinates in boundary_values:
            # Generate a new image file for each request
            image_data = BytesIO()
            image = Image.new("RGB", (416, 416), color="blue")
            image.save(image_data, format="JPEG")
            image_data.seek(0)  # Reset the buffer to the beginning

            data = {
                'file': (image_data, 'boundary_image.jpg'),
                'latitude': str(coordinates["latitude"]),
                'longitude': str(coordinates["longitude"])
            }

            # Send the POST request with boundary latitude/longitude
            response = self.client.post('/upload_frame', data=data, headers={
                'Authorization': f'Bearer {token}'
            }, content_type='multipart/form-data')

            self.assertEqual(response.status_code, 200, f"Failed for coordinates: {coordinates}")

    def test_upload_frame_inverted_auth_format(self):
        # Set up test data with a valid image and location data
        image_data = BytesIO()
        image = Image.new("RGB", (416, 416), color="yellow")
        image.save(image_data, format="JPEG")
        image_data.seek(0)  # Reset the buffer for reading

        data = {
            'file': (image_data, 'inverted_auth_image.jpg'),
            'latitude': '47.494367',
            'longitude': '19.060115'
        }

        # Send request with inverted authorization format
        token = self.get_valid_token()
        response = self.client.post('/upload_frame', data=data, headers={
            'Authorization': f'Token {token}'
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['error'])
