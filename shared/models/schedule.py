from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
    course_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    start_date: Mapped[str] = mapped_column(
        DateTime,
        nullable=False,
    )
    end_date: Mapped[str] = mapped_column(
        DateTime,
        nullable=False,
    )
    location: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    course_mode_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    created_by: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_by: Mapped[str | None] = mapped_column(
        String,
    )
    updated_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True),
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

    @classmethod
    def get_detail(cls, schedule_id: str) -> "Schedule | None":
        return db.session.query(cls).filter(cls.id == schedule_id).first()
