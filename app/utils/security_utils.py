from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
    )
    return encoded_jwt
