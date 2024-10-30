from flask import g
from db.db_connection import Database
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

class Auth:
    def __init__(self, token):
        self.token = token

    def verify_token(self):
        """
        Verifies the JWT token and sets the user ID in the Flask global `g` object.
        """
        try:
            verify_jwt_in_request()  # Verifies the JWT token
            user_id = get_jwt_identity()  # Extracts the user ID from the JWT
            g.user_id = user_id
            return True
        except Exception as e:
            print(f"Token verification failed: {e}")
            return False

    def get_user_id_from_token(self):
        """
        Returns the user ID from the token if it's valid, or None if it's invalid.
        """
        try:
            # Check if the token is already verified and user_id is in g
            if hasattr(g, 'user_id'):
                return g.user_id

            # If not already verified, manually extract the user ID from the token
            verify_jwt_in_request()  # Verifies the JWT token
            user_id = get_jwt_identity()  # Extracts the user ID from the JWT
            return user_id
        except Exception as e:
            print(f"Error extracting user_id from token: {e}")
            return None

    def get_user_role(self):
        conn = Database.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_role_name 
                FROM user_role 
                INNER JOIN "user" ON "user".user_role_id = user_role.user_role_id
                WHERE user_id = %s
            """, (g.user_id,))
            result = cursor.fetchone()
            cursor.close()
            Database.return_connection(conn)
            return result[0] if result else None
        return None
