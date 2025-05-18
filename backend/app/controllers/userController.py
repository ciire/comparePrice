from flask import request, jsonify
from app.services.user import create_user, edit_user  

def create_user_controller():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    password = data.get("password")
    notification_settings = data.get("notification_settings", {})
    tracked_items = data.get("tracked_items", [])

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    result = create_user(email, password, notification_settings, tracked_items)

    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 400

    return jsonify({"status": "success", "user_id": result}), 201


def edit_user_controller(user_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    result, status_code = edit_user(user_id, data)
    return jsonify(result), status_code
