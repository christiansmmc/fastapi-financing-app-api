from fastapi import APIRouter, HTTPException

from app.deps import SessionDep
from app.repository.users import get_user_by_email, create_user
from app.schemas import UserCreate, UserPublic

router = APIRouter()


@router.post("", tags=["users"], response_model=UserPublic)
def create_user_endpoint(session: SessionDep, user: UserCreate):
    existent_user = get_user_by_email(session, user.email)
    if existent_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    return create_user(session, user)
