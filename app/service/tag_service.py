from sqlmodel import Session

from app.repository.tag_repository import TagRepository


class TagService:
    def __init__(self, session: Session):
        self.session = session
        self.tag_repository = TagRepository(session)

    def get_tags(self):
        return self.tag_repository.get_all_tags()
