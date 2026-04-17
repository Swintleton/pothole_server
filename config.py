import os
from datetime import timedelta

# Configuration variables
SERVER_IP = os.getenv("SERVER_IP", "0.0.0.0") #192.168.0.115
SERVER_PORT = os.getenv("SERVER_PORT", "5000")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "pothole")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES", timedelta(minutes=15))
JWT_REFRESH_TOKEN_EXPIRES = os.getenv("JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=30))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_DATABASE = os.getenv("DB_DATABASE", "pothole")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_NAME = os.getenv("DB_NAME", "database_name")
