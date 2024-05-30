from collections.abc import Generator
from typing import Annotated

import jwt
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.config.db import engine
from app.schemas import TokenPayload
from app.models import Users
from app.repository.users import get_user_by_email

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> Users:
    try:
        secret_key = os.getenv("JWT_SECRET_KEY")
        algorithm = os.getenv("JWT_ALGORITHM")

        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = get_user_by_email(session, token_data.sub)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")

    return user


CurrentUser = Annotated[Users, Depends(get_current_user)]
