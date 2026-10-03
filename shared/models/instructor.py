import uuid_extensions
from sqlalchemy import Boolean, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Instructor(Base):
    __tablename__ = "instructor"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    phone_number: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    course_theme_id: Mapped[str] = mapped_column(String, nullable=False)
    specialization: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    deleted_at: Mapped[str | None] = mapped_column(DateTime)
    deleted_by: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    created_by: Mapped[str] = mapped_column(String)
    updated_at: Mapped[str | None] = mapped_column(DateTime)
    updated_by: Mapped[str | None] = mapped_column(String)

    def __init__(
        self,
        name: str,
        phone_number: str,
        email: str,
        course_theme_id: str,
        specialization: str,
        created_at: str,
        created_by: str,
        is_deleted: bool = False,
        updated_at: str | None = None,
        updated_by: str | None = None,
        deleted_at: str | None = None,
        deleted_by: str | None = None,
    ):
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.course_theme_id = course_theme_id
        self.specialization = specialization
        self.is_deleted = is_deleted
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by

    @classmethod
    def get_detail(cls, instructor_id: str) -> "Instructor | None":
        return db.session.query(cls).filter(cls.id == instructor_id).first()
