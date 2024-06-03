import os
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext


class AuthUtils:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm = os.getenv("JWT_ALGORITHM")
    jwt_access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return AuthUtils.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return AuthUtils.pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict):
        print(f"JWT Access Token Expire Minutes: {AuthUtils.jwt_access_token_expire_minutes}")

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=AuthUtils.jwt_access_token_expire_minutes
        )

        print(f"Token expiration time: {expire}")

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, AuthUtils.jwt_secret_key, algorithm=AuthUtils.jwt_algorithm
        )
        return encoded_jwt
