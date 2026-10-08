import uuid_extensions
from sqlalchemy import Boolean, DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Course(Base):
    __tablename__ = "course"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    course_related_id: Mapped[str | None] = mapped_column(String)
    sanity_id: Mapped[str] = mapped_column(String)
    course_type_id: Mapped[str] = mapped_column(String)
    course_class_type_id: Mapped[str] = mapped_column(String)
    course_theme_id: Mapped[str] = mapped_column(String)
    course_certificate_validity_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    asset_status: Mapped[str] = mapped_column(
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
    deleted_at: Mapped[str | None] = mapped_column(DateTime)
    deleted_by: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    created_by: Mapped[str] = mapped_column(String)
    updated_at: Mapped[str | None] = mapped_column(DateTime)
    updated_by: Mapped[str | None] = mapped_column(String)

    def __init__(
        self,
        course_related_id: str | None,
        sanity_id: str,
        course_type_id: str,
        course_class_type_id: str,
        course_theme_id: str,
        course_certificate_validity_id: str,
        name: str,
        asset_status: str,
        slug: str,
        duration: int,
        overview: str,
        objective: str,
        outline: str,
        requirement: str,
        is_fresh_graduate: bool,
        is_experienced: bool,
        is_student: bool,
        created_at: str,
        created_by: str,
        is_deleted: bool = False,
        updated_at: str | None = None,
        updated_by: str | None = None,
        deleted_at: str | None = None,
        deleted_by: str | None = None,
    ):
        self.sanity_id = sanity_id
        self.course_related_id = course_related_id
        self.sanity_id = sanity_id
        self.course_type_id = course_type_id
        self.course_class_type_id = course_class_type_id
        self.course_theme_id = course_theme_id
        self.course_certificate_validity_id = course_certificate_validity_id
        self.name = name
        self.asset_status = asset_status
        self.slug = slug
        self.duration = duration
        self.overview = overview
        self.objective = objective
        self.outline = outline
        self.requirement = requirement
        self.is_fresh_graduate = is_fresh_graduate
        self.is_experienced = is_experienced
        self.is_student = is_student
        self.is_deleted = is_deleted
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by

    @classmethod
    def get_detail(cls, course_id: str) -> "Course | None":
        return db.session.get(cls, course_id)
