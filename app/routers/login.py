from fastapi import APIRouter, HTTPException

from app.deps import SessionDep
from app.repository.users import get_user_by_email
from app.schemas import Login, Token
from app.utils.security_utils import verify_password, create_access_token

router = APIRouter()


@router.post("/", tags=["login"], response_model=Token)
def login(session: SessionDep, login_data: Login):
    user = get_user_by_email(session, login_data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    verify_password(login_data.password, user.password)

    access_token = create_access_token(data={"sub": user.email})

    return Token(access_token=access_token)
