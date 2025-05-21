from flask import request, jsonify
from app.services.user import initiate_signup, edit_user, verify_signup_code
def signup_user_controller():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        email = data.get("email")
        password = data.get("password")
        notification_settings = data.get("notification_settings", {})
        tracked_items = data.get("tracked_items", [])

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        result = initiate_signup(email, password, notification_settings, tracked_items)

        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 400

        return jsonify({"status": "success", "user_id": result}), 201
    except Exception as e:
        print(f"Unexpected error during signup: {e}")
        return jsonify({"error": "Internal server error"}), 500
def verify_signup_code_controller():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        email = data.get("email")
        code = data.get("code")
        token = data.get("token")

        if not email or not code:
            return jsonify({"error": "Email and verification code are required"}), 400

        result = verify_signup_code(email, code, token)

        if isinstance(result, tuple):  # Handles (dict, status_code)
            return jsonify(result[0]), result[1]

        return jsonify(result), 200
    except Exception as e:
        print(f"Unexpected error in verify signup code: {e}")
        return jsonify({"error": "Internal server error"}), 500

def edit_user_controller(user_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        result, status_code = edit_user(user_id, data)
        return jsonify(result), status_code
    except Exception as e:
        print(f"Unexpected error in edit user controller: {e}")
        return jsonify({"error": "Internal server error"}), 500
