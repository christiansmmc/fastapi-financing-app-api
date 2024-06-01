from fastapi import HTTPException
from sqlmodel import Session

from app.repository.user_repository import UserRepository
from app.schemas import Login, Token
from app.utils.security_utils import AuthUtils


class LoginService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repository = UserRepository(session)

    def login(self, login_data: Login):
        user = self.user_repository.get_user_by_email(login_data.email)

        if not user:
            raise HTTPException(status_code=401, detail="Email ou senha inválidos")

        AuthUtils.verify_password(login_data.password, user.password)

        access_token = AuthUtils.create_access_token(data={"sub": user.email})

        return Token(access_token=access_token)
