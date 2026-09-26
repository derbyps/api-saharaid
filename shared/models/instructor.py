from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, func, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Instructor(Base):
    __tablename__ = "instructor"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
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

    course_theme_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("public.course_theme.id"),
        nullable=False,
    )

    specialization: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    deleted_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    deleted_by: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("public.users.id")
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False
    )
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    updated_by: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("public.users.id")
    )

    @classmethod
    def get_detail(cls, instructor_id: str) -> "Instructor | None":
        return db.session.query(cls).filter(cls.id == instructor_id).first()
