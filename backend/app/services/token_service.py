import os
import jwt
from datetime import datetime, timezone, timedelta

JWT_SECRET = os.getenv("APP_SECRET_KEY", "fallback-dev-secret")
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 10

def create_verification_token(email, code):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MINUTES)
    payload = {
        "email": email,
        "code": code,
        "exp": expiration,
        "purpose": "email_verification"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_verification_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("purpose") != "email_verification":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        print("Verification token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid verification token: {e}")
        return None

