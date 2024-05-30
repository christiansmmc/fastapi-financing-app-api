from typing import List

from fastapi import APIRouter

from app.deps import SessionDep, CurrentUser
from app.repository.tags import get_all_tags
from app.schemas import TagPublic

router = APIRouter()


@router.get("", tags=["tags"], response_model=List[TagPublic])
def get_tags_endpoint(session: SessionDep, current_user: CurrentUser):
    return get_all_tags(session)
