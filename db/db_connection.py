import psycopg2

class Database:
    @staticmethod
    def get_connection():
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="pothole",
                user="postgres",
                password="123456"
            )
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None