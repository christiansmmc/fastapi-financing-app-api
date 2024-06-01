from fastapi import HTTPException
from sqlmodel import Session

from app.repository.user_repository import UserRepository
from app.schemas import UserCreate


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repository = UserRepository(session)

    def create_user(self, user: UserCreate):
        existent_user = self.user_repository.get_user_by_email(user.email)
        if existent_user:
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        return self.user_repository.create_user(user)
