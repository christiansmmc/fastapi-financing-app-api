from sqlmodel import Session, select

from app.models import Users
from app.schemas import UserCreate
from app.utils.security_utils import AuthUtils


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str):
        search_user = select(Users).where(Users.email == email)
        return self.session.exec(search_user).first()

    def create_user(self, user: UserCreate):
        db_user = Users.model_validate(
            user, update={"password": AuthUtils.get_password_hash(user.password)}
        )

        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

        return db_user
