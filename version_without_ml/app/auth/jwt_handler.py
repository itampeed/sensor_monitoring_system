import os

# Use this value to match against the token string sent by the client
SECRET_KEY = os.getenv("JWT_SECRET", "mP@9z!rV6q#fY2bL$uX8sK%J3tW0gE")

def verify_jwt(token):
    return token == SECRET_KEY
