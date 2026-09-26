import uuid_extensions
from sqlalchemy import Boolean, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Course(Base):
    __tablename__ = "course"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    type_id: Mapped[str] = mapped_column(String)
    mode_id: Mapped[str] = mapped_column(String)
    course_theme_id: Mapped[str] = mapped_column(String)
    course_related_id: Mapped[str | None] = mapped_column(String)
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    certificate_validity: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    overview: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    objective: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    outline: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    requirement: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    brochure: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    is_fresh_graduate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_experienced: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_student: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    deleted_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    deleted_by: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[str] = mapped_column(String)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    updated_by: Mapped[str | None] = mapped_column(String)

    @classmethod
    def get_detail(cls, course_id: str) -> "Course | None":
        return db.session.get(cls, course_id)
