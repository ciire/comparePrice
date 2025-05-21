from datetime import datetime, timezone, timedelta
import random
from app.db.mongo_client import db
import bcrypt
from bson import ObjectId
from bson.errors import InvalidId
from marshmallow import ValidationError

from app.services.email_service import send_verification_email
from app.services.token_service import create_verification_token, decode_verification_token

from app.validation.schemas import CreateUserSchema


users_collection = db["users"]
pending_users_collection = db["pending_users"]
user_schema = CreateUserSchema()

def generate_verification_code():
    return str(random.randint(100000, 999999))

def initiate_signup(email, password, notification_settings=None, tracked_items=None):
    try:
        validated_data = user_schema.load({
            "email": email,
            "password": password,
            "notification_settings": notification_settings,
            "tracked_items": tracked_items
        })

        if users_collection.find_one({"email": email}) or pending_users_collection.find_one({"email": email}):
            return {"error": "If you're eligible to sign up, we’ll send you a verification email soon."}

        password_hash = bcrypt.hashpw(validated_data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        verification_code = generate_verification_code()
        jwt_token = create_verification_token(email, verification_code)

        # Store user data temporarily in pending_users
        pending_users_collection.insert_one({
            "email": email,
            "passwordHash": password_hash,
            "notificationSettings": validated_data.get("notification_settings", {}),
            "trackedItems": validated_data.get("tracked_items", []),
            "createdAt": datetime.now(timezone.utc)
        })

        send_verification_email(email, verification_code)
        return {"message": "Verification code sent to email", "token": jwt_token}
    except ValidationError as err:
        return {"error": "Invalid input", "details": err.messages}
    except Exception as e:
        print(f"Unexpected error during signup: {e}")
        return {"error": "Internal server error"}, 500

def verify_signup_code(email, code, token):
    try:
        payload = decode_verification_token(token)
        if not payload:
            return {"error": "Invalid or expired token"}, 400

        if payload.get("email") != email or payload.get("code") != code:
            return {"error": "Email or code mismatch"}, 400

        # Retrieve pending user data
        pending_user = pending_users_collection.find_one({"email": email})
        if not pending_user:
            return {"error": "Verification data not found"}, 404

        user_document = {
            "email": pending_user["email"],
            "passwordHash": pending_user["passwordHash"],
            "notificationSettings": pending_user.get("notificationSettings", {}),
            "trackedItems": pending_user.get("trackedItems", [])
        }

        # Insert into main users collection
        result = users_collection.insert_one(user_document)

        # Remove from pending
        pending_users_collection.delete_one({"email": email})

        return {"status": "success", "user_id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error verifying signup: {e}")
        return {"error": "Internal server error"}, 500
    
def edit_user(user_id, update_data):
    try:
        user_object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        return {"error": "Invalid user ID format"}, 400

    try:
        # Only validate provided fields
        partial_schema = CreateUserSchema(partial=True)
        validated_data = partial_schema.load(update_data)
    except ValidationError as err:
        return {"error": "Invalid input", "details": err.messages}, 400

    update_fields = {}

    if "password" in validated_data:
        update_fields["passwordHash"] = bcrypt.hashpw(
            validated_data["password"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    if "email" in validated_data:
        update_fields["email"] = validated_data["email"]

    if "notification_settings" in validated_data:
        update_fields["notificationSettings"] = validated_data["notification_settings"]

    if "tracked_items" in validated_data:
        update_fields["trackedItems"] = validated_data["tracked_items"]

    if not update_fields:
        return {"error": "No valid fields to update"}, 400
    try:
        result = users_collection.update_one(
            {"_id": user_object_id},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            return {"error": "User not found"}, 404

        return {"status": "success", "modified_count": result.modified_count}, 200
    except Exception as e:
        print(f"Failed to update user {user_id}: {e}")
        return {"error": "Internal server error"}, 500