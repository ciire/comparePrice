from app.db.mongo_client import db
import bcrypt
from marshmallow import ValidationError

from app.validation.schemas import CreateUserSchema

users_collection = db["users"]
user_schema = CreateUserSchema()

def create_user(email, password, notification_settings={}, tracked_items=[]):
    # Validate input
    try:
        validated_data = user_schema.load({
            "email": email,
            "password": password,
            "notification_settings": notification_settings,
            "tracked_items": tracked_items
        })
    except ValidationError as err:
        return {"error": "Invalid input", "details": err.messages}
    password_hash = bcrypt.hashpw(validated_data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user_document = {
        "email": validated_data["email"],
        "passwordHash": password_hash,
        "notificationSettings": validated_data.get("notification_settings", {}),
        "trackedItems": validated_data.get("tracked_items", [])
    }

    result = users_collection.insert_one(user_document)
    return str(result.inserted_id)