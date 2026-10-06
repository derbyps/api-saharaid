import uuid_extensions
from sqlalchemy import Boolean, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class CourseTheme(Base):
    __tablename__ = "course_theme"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    sanity_id: Mapped[str | None] = mapped_column(String)
    title: Mapped[str | None] = mapped_column(Text)
    slug: Mapped[str | None] = mapped_column(Text)
    synced_at: Mapped[str | None] = mapped_column(DateTime)
    created_at: Mapped[str | None] = mapped_column(DateTime)
    created_by: Mapped[str | None] = mapped_column(String)
    updated_at: Mapped[str | None] = mapped_column(DateTime)
    updated_by: Mapped[str | None] = mapped_column(String)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    deleted_at: Mapped[str | None] = mapped_column(DateTime)
    deleted_by: Mapped[str | None] = mapped_column(String)

    def __init__(
        self,
        sanity_id: str | None = None,
        title: str | None = None,
        slug: str | None = None,
        synced_at: str | None = None,
        created_at: str | None = None,
        created_by: str | None = None,
        updated_at: str | None = None,
        updated_by: str | None = None,
        is_deleted: bool = False,
        deleted_at: str | None = None,
        deleted_by: str | None = None,
    ):
        self.sanity_id = sanity_id
        self.title = title
        self.slug = slug
        self.synced_at = synced_at
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.is_deleted = is_deleted
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by

    @classmethod
    def get_detail(cls, course_theme_id: str) -> "CourseTheme | None":
        return db.session.get(cls, course_theme_id)
