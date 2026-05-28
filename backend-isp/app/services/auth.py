# app/services/auth.py
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

ph = PasswordHasher()

def get_password_hash(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    # BUENA PRÁCTICA: Si no viene un delta específico, usa el del .env por defecto
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generar_tokens_login(username: str):
    # Usamos la variable del .env leída al inicio del archivo
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.utcnow() + expires_delta

    access_token = create_access_token(data={"sub": username}, expires_delta=expires_delta)
    refresh_token = create_access_token(data={"sub": username}, expires_delta=timedelta(days=7))

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresAt": expires_at.isoformat() + "Z"
    }