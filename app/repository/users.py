from sqlmodel import Session, select

from app.models import Users
from app.schemas import UserCreate
from app.utils.security_utils import get_password_hash


def get_user_by_email(session: Session, email: str):
    search_user = select(Users).where(Users.email == email)
    return session.exec(search_user).first()


def create_user(session: Session, user: UserCreate):
    db_user = Users.model_validate(
        user, update={"password": get_password_hash(user.password)}
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user
