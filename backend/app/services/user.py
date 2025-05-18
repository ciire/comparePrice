from app.db.mongo_client import db
import bcrypt
from bson import ObjectId
from bson.errors import InvalidId
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

    result = users_collection.update_one(
        {"_id": user_object_id},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return {"error": "User not found"}, 404

    return {"status": "success", "modified_count": result.modified_count}, 200