from flask import g
from db.db_connection import Database

class Auth:
    def __init__(self, token):
        self.token = token

    def verify_token(self):
        if self.token == "fake_token":  # Replace this with real token validation
            conn = Database.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM \"user\" WHERE user_login = 'admin'")
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                if user:
                    g.user_id = user[0]
                    return True
        return False
