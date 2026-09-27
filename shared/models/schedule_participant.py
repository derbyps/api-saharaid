import uuid_extensions
from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base


class ScheduleParticipant(Base):
    __tablename__ = "schedule_participant"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )

    schedule_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    participant_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
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

    updated_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True),
    )

    updated_by: Mapped[str | None] = mapped_column(
        String,
    )

    deleted_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True),
    )

    deleted_by: Mapped[str | None] = mapped_column(
        String,
    )
