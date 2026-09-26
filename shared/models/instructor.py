import uuid_extensions
from sqlalchemy import Boolean, DateTime, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Instructor(Base):
    __tablename__ = "instructor"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    phone_number: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    course_theme_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    specialization: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    deleted_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True),
    )

    deleted_by: Mapped[str | None] = mapped_column(
        String,
    )

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    created_by: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    updated_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True),
    )

    updated_by: Mapped[str | None] = mapped_column(
        String,
    )

    @classmethod
    def get_detail(cls, instructor_id: str) -> "Instructor | None":
        return db.session.query(cls).filter(cls.id == instructor_id).first()
