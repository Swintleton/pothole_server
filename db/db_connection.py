import psycopg2
from psycopg2 import pool

from unittest.mock import MagicMock

class Database:
    connection_pool = None

    @staticmethod
    def init_pool():
        if Database.connection_pool is None:
            Database.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=20,  # Adjust this based on your expected load
                host="localhost",
                database="pothole",
                user="postgres",
                password="123456"
            )

    @staticmethod
    def get_connection():
        try:
            if Database.connection_pool is None:
                Database.init_pool()
            conn = Database.connection_pool.getconn()
            return conn
        except Exception as e:
            logger.info(f"Database connection error: {e}")
            return None

    @staticmethod
    def return_connection(conn):
        if conn and not isinstance(conn, MagicMock):
            Database.connection_pool.putconn(conn)

    @staticmethod
    def close_all_connections():
        Database.connection_pool.closeall()
