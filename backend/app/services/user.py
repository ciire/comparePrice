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
import jwt

#rate limiting and use JWT to store verification instead of MongoDB

users_collection = db["users"]
pending_users_collection = db["pending_users"]
user_schema = CreateUserSchema()

JWT_SECRET = os.getenv("APP_SECRET_KEY", "fallback-dev-secret")
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 3

def create_verification_token(email):
    try:
        expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MINUTES)
        payload = {
            "email": email,
            "exp": expiration,
            "purpose": "email_verification"
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    except Exception as e: 
        print(f"Failed to create JWT token: {e}")
        return None
def decode_verification_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("purpose") != "email_verification":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        print(f"Verification token expired")
        return None
    except jwt.InvalidTokenError:
        print(f"Invalid verification token: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error decoding token: {e}")
        return None

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = os.getenv("GMAIL_USERNAME")
        smtp_password = os.getenv("GMAIL_APP_PASSWORD")

        # Test line to see if it works
        if not smtp_username or not smtp_password:
            print("SMTP credentials not found in environment variables.")
            return False
        
        subject = "Your Email Verification Code"
        link = f"https://localhost.com/"
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

        pending_user = {
            "email": validated_data["email"],
            "passwordHash": password_hash,
            "notificationSettings": validated_data.get("notification_settings", {}),
            "trackedItems": validated_data.get("tracked_items", []),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MINUTES),
            "purpose": "email_verification",
            "code": verification_code
        }
        
        jwt_token = jwt.encode(pending_user, JWT_SECRET, algorithm=JWT_ALGORITHM)
        send_verification_email(email, verification_code)
        return {"message": "Verification code sent to email",
                "token": jwt_token}
    except ValidationError as err:
        return {"error": "Invalid input", "details": err.messages}
    except Exception as e:
        print(f"Unexpected error during signup: {e}")
        return {"error": "Internal server error"}, 500

def verify_signup_code(email, code, token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


        if payload.get("purpose") != "email_verification":
            return {"error": "Invalid token purpose"}, 400

        if payload.get("email") != email:
            return {"error": "Email mismatch"}, 400

        if payload.get("code") != code:
            return {"error": "Invalid code"}, 400

        # Move user into users collection
        user_document = {
            "email": payload["email"],
            "passwordHash": payload["passwordHash"],
            "notificationSettings": payload.get("notificationSettings", {}),
            "trackedItems": payload.get("trackedItems", [])
        }

        result = users_collection.insert_one(user_document)

        return {"status": "success", "user_id": str(result.inserted_id)}
    except jwt.ExpiredSignatureError:
        return {"error": "Verification expired"}, 400
    except jwt.InvalidTokenError:
        return {"error": "Invalid verification data"}, 400
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