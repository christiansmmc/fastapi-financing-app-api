from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Tag


def get_tag_by_id(session: Session, tag_id: int):
    search_tag = select(Tag).where(Tag.id == tag_id)
    tag = session.exec(search_tag).first()

    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    return tag


def get_all_tags(session: Session):
    search_tag = select(Tag)
    return session.exec(search_tag).all()
