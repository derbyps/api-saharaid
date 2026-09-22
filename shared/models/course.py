from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Course(Base):
    __tablename__ = "course"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    type_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("public.course_type.id"),
        nullable=False,
    )

    mode_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("public.course_mode.id"),
        nullable=False,
    )

    course_theme_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("public.course_theme.id"),
        nullable=False,
    )

    course_related_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("public.course.id"),
    )

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
    def get_detail(cls, course_id: UUID) -> "Course | None":
        return db.session.get(cls, course_id)
