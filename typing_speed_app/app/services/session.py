from fastapi import Request, Response
from itsdangerous import URLSafeSerializer
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")  # ajoute-le dans .env
SESSION_NAME = "session"

serializer = URLSafeSerializer(SECRET_KEY)

def set_session(response: Response, user_id: int):
    session_token = serializer.dumps({"user_id": user_id})
    response.set_cookie(key=SESSION_NAME, value=session_token, httponly=True)

def get_session_user(request: Request):
    session_token = request.cookies.get(SESSION_NAME)
    if session_token:
        try:
            data = serializer.loads(session_token)
            return data.get("user_id")
        except Exception:
            return None
    return None

def clear_session(response: Response):
    response.delete_cookie(SESSION_NAME)
