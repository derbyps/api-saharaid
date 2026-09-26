import uuid_extensions
from sqlalchemy import BINARY, Boolean, DateTime, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Course(Base):
    __tablename__ = "course"

    id: Mapped[bytes] = mapped_column(
        BINARY(16),
        primary_key=True,
        default=lambda: uuid_extensions.uuid7(as_type="bytes"),
    )
    type_id: Mapped[bytes] = mapped_column(BINARY)
    mode_id: Mapped[bytes] = mapped_column(BINARY)
    course_theme_id: Mapped[bytes] = mapped_column(BINARY)
    course_related_id: Mapped[bytes | None] = mapped_column(BINARY)
    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    certificate_validity: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    overview: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    outline: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    requirement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    brochure: Mapped[str] = mapped_column(
        Text,
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
    deleted_by: Mapped[bytes] = mapped_column(BINARY)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[bytes] = mapped_column(BINARY)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    updated_by: Mapped[bytes | None] = mapped_column(BINARY)

    @classmethod
    def get_detail(cls, course_id: str) -> "Course | None":
        return db.session.get(cls, course_id)
