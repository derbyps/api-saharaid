import uuid_extensions
from sqlalchemy import Boolean, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base


class ScheduleParticipant(Base):
    __tablename__ = "schedule_participant"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    schedule_id: Mapped[str] = mapped_column(String, nullable=False)
    participant_id: Mapped[str] = mapped_column(String, nullable=False)
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
        schedule_id: str,
        participant_id: str,
        created_at: str,
        created_by: str,
        is_deleted: bool = False,
        updated_at: str | None = None,
        updated_by: str | None = None,
        deleted_at: str | None = None,
        deleted_by: str | None = None,
    ):
        self.schedule_id = schedule_id
        self.participant_id = participant_id
        self.is_deleted = is_deleted
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by
