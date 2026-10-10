import uuid_extensions
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class CourseRelated(Base):
    __tablename__ = "course_related"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    course_id: Mapped[str] = mapped_column(String)
    course_related_id: Mapped[str] = mapped_column(String)

    def __init__(
        self,
        course_id: str,
        course_related_id: str,
    ):
        self.course_id = course_id
        self.course_related_id = course_related_id

    @classmethod
    def get_detail(cls, id: str) -> "CourseRelated | None":
        return db.session.get(cls, id)
