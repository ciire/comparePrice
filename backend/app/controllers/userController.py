from flask import request, jsonify
from app.services.user import initiate_signup, edit_user, verify_code

def handle_service_response(result, default_status_code=200):
    if isinstance(result, tuple) and len(result) == 2:
        data, status_code = result
        return jsonify(data), status_code

    if isinstance(result, dict):
        status_code = result.pop("status_code", None)
        if "error" in result and not status_code:
            status_code = 400
        return jsonify(result), status_code or default_status_code

    # Fallback for unexpected types
    return jsonify({"error": "Invalid service response format"}), 500

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
        return handle_service_response(result, default_status_code=201)

    except Exception as e:
        print(f"Unexpected error during signup: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
def verify_code_controller():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        email = data.get("email")
        code = data.get("code")
        token = data.get("token")
        purpose = data.get("purpose", "email_verification")

        if not email or not code or not token:
            return jsonify({"error": "Email, verification code, and token are required"}), 400

        result = verify_code(email, code, token, purpose)
        return handle_service_response(result)

    except Exception as e:
        print(f"Unexpected error in verify_code_controller: {e}")
        return jsonify({"error": "Internal server error"}), 500


def edit_user_controller(user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        result = edit_user(user_id, data)
        return handle_service_response(result)

    except Exception as e:
        print(f"Unexpected error in edit user controller: {e}")
        return jsonify({"error": "Internal server error"}), 500
