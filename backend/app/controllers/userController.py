from flask import request, jsonify
from app.services.user import initiate_signup, edit_user, send_verification_email, generate_verification_code, verify_signup_code
def signup_user_controller():
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

def send_verification_email_controller():
    data = request.get_json()

    if not data or not data.get("email"):
        return jsonify({"error": "Email is required"}), 400

    email = data["email"]
    code = generate_verification_code()

    success = send_verification_email(email, code)
    if success:
        return jsonify({"status": "success", "message": "Verification email sent"}), 200
    else:
        return jsonify({"status": "failure", "message": "Failed to send verification email"}), 500
    
def verify_signup_code_controller():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"error": "Email and verification code are required"}), 400

    result = verify_signup_code(email, code)

    if isinstance(result, tuple):  # Handles (dict, status_code)
        return jsonify(result[0]), result[1]

    return jsonify(result), 200

def edit_user_controller(user_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    result, status_code = edit_user(user_id, data)
    return jsonify(result), status_code
