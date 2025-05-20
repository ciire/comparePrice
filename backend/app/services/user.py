from datetime import datetime, timezone, timedelta
import random
import uuid
from app.db.mongo_client import db
import bcrypt
from bson import ObjectId
from bson.errors import InvalidId
from marshmallow import ValidationError

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.validation.schemas import CreateUserSchema

users_collection = db["users"]
pending_users_collection = db["pending_users"]
user_schema = CreateUserSchema()

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv("GMAIL_USERNAME")
    smtp_password = os.getenv("GMAIL_APP_PASSWORD")

    # Test line to see if it works
    if not smtp_username or not smtp_password:
        print("SMTP credentials not found in environment variables.")
        return False
    
    subject = "Your Email Verification Code"
    body = f"""
    Hello,

    Thank you for signing up. Please use the following code to verify your email address:

    🔐 Verification Code: {code}

    This code is valid for the next 10 minutes.

    If you did not request this, you can ignore this message.

    -- Your App Team
    """

    # Compose email
    message = MIMEMultipart()
    message["From"] = smtp_username
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()  # Secure the connection
            server.login(smtp_username, smtp_password)
            server.send_message(message)
        print(f"Verification email sent to {email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def initiate_signup(email, password, notification_settings={}, tracked_items=[]):
    try:
        validated_data = user_schema.load({
            "email": email,
            "password": password,
            "notification_settings": notification_settings,
            "tracked_items": tracked_items
        })
    except ValidationError as err:
        return {"error": "Invalid input", "details": err.messages}
    
    if users_collection.find_one({"email": email}) or pending_users_collection.find_one({"email": email}):
        return {"error": "Email already in use or pending verification"}

    password_hash = bcrypt.hashpw(validated_data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    verification_code = generate_verification_code()

    pending_user = {
        "email": validated_data["email"],
        "passwordHash": password_hash,
        "notificationSettings": validated_data.get("notification_settings", {}),
        "trackedItems": validated_data.get("tracked_items", []),
        "verificationCode": verification_code,
        "expiresAt": datetime.now(timezone.utc) + timedelta(minutes=3)
    }
    
    pending_users_collection.insert_one(pending_user)
    send_verification_email(email, verification_code)
    return {"message": "Verification code sent to email"}

def verify_signup_code(email, code):
    pending_user = pending_users_collection.find_one({"email": email})

    if not pending_user:
        return {"error": "No pending verification for this email"}, 404

    if pending_user["verificationCode"] != code:
        return {"error": "Invalid verification code"}, 400
    expires_at = pending_user["expiresAt"]

    # Make it timezone-aware if MongoDB returned it as naive
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        pending_users_collection.delete_one({"_id": pending_user["_id"]})
        return {"error": "Verification code expired"}, 400

    # Move to real users collection
    user_document = {
        "email": pending_user["email"],
        "passwordHash": pending_user["passwordHash"],
        "notificationSettings": pending_user.get("notificationSettings", {}),
        "trackedItems": pending_user.get("trackedItems", []),
    }

    result = users_collection.insert_one(user_document)
    pending_users_collection.delete_one({"_id": pending_user["_id"]})

    return {"status": "success", "user_id": str(result.inserted_id)}

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