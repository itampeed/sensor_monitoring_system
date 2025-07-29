import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET", "mP@9z!rV6q#fY2bL$uX8sK%J3tW0gE")
ALGORITHM = "HS256"

def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # You can extend this by checking exp, iss, aud if needed
        return payload
    except jwt.ExpiredSignatureError:
        print("[JWT] Token expired.")
        return False
    except jwt.InvalidTokenError:
        print("[JWT] Invalid token.")
        return False

def extract_client_id(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("client_id")
    except jwt.InvalidTokenError:
        return None

def create_jwt(client_id, expires_in=24*3600):
    payload = {
        "client_id": client_id,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
