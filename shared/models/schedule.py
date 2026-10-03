import uuid_extensions
from sqlalchemy import BigInteger, Boolean, DateTime, Identity, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    course_id: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    course_mode_id: Mapped[str] = mapped_column(String, nullable=False)
    serial_number: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), unique=True
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
        course_id: str,
        start_date: str,
        end_date: str,
        location: str,
        course_mode_id: str,
        serial_number: int,
        created_at: str,
        created_by: str,
        is_deleted: bool = False,
        updated_at: str | None = None,
        updated_by: str | None = None,
        deleted_at: str | None = None,
        deleted_by: str | None = None,
    ):
        self.course_id = course_id
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.course_mode_id = course_mode_id
        self.serial_number = serial_number
        self.is_deleted = is_deleted
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by

    @classmethod
    def get_detail(cls, schedule_id: str) -> "Schedule | None":
        return db.session.query(cls).filter(cls.id == schedule_id).first()
