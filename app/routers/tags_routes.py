from typing import List

from fastapi import APIRouter

from app.deps import SessionDep, CurrentUser
from app.schemas import TagPublic
from app.service.tag_service import TagService

router = APIRouter()


@router.get("", tags=["tags"], response_model=List[TagPublic])
def get_tags_endpoint(session: SessionDep, current_user: CurrentUser):
    tag_service = TagService(session)
    return tag_service.get_tags()
