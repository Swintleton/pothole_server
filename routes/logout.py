from flask import Blueprint, jsonify, g
from db.db_connection import Database

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Invalidate or remove the token (for now we assume it's just removed from the client side)
        # For a real scenario, you could implement token blacklisting or deletion from the server
        
        g.user_id = None  # Remove user context for this session if applicable
        return jsonify({"message": "Logout successful"}), 200
    except Exception as e:
        print(f"Error during logout: {e}")
        return jsonify({'error': 'Error during logout'}), 500
