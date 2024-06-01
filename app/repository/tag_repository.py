from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Tag


class TagRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_tag_by_id(self, tag_id: int):
        search_tag = select(Tag).where(Tag.id == tag_id)
        tag = self.session.exec(search_tag).first()

        if tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")

        return tag

    def get_all_tags(self):
        search_tag = select(Tag)
        return self.session.exec(search_tag).all()
