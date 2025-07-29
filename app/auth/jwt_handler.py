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
