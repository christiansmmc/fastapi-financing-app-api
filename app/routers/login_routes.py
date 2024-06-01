from fastapi import APIRouter

from app.deps import SessionDep
from app.schemas import Login, Token
from app.service.login_service import LoginService

router = APIRouter()


@router.post("", tags=["login"], response_model=Token)
def login(session: SessionDep, login_data: Login):
    login_service = LoginService(session)
    return login_service.login(login_data)
