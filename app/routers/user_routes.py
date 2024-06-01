from fastapi import APIRouter

from app.deps import SessionDep
from app.schemas import UserCreate, UserPublic
from app.service.user_service import UserService

router = APIRouter()


@router.post("", tags=["users"], response_model=UserPublic)
def create_user_endpoint(session: SessionDep, user: UserCreate):
    user_service = UserService(session)
    return user_service.create_user(user)
