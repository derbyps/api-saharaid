import uuid_extensions
from sqlalchemy import BigInteger, Boolean, Date, DateTime, Identity, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base, db


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    identity_number: Mapped[str] = mapped_column(String, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[str] = mapped_column(Date, nullable=False)
    religion: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    job_position: Mapped[str] = mapped_column(String, nullable=False)
    job_company: Mapped[str] = mapped_column(String, nullable=False)
    education: Mapped[str] = mapped_column(String, nullable=False)
    cr_number: Mapped[str] = mapped_column(String, nullable=False)
    tax_number: Mapped[str] = mapped_column(String, nullable=False)
    serial_number: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), unique=True
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    deleted_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    deleted_by: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[str] = mapped_column(String)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    updated_by: Mapped[str | None] = mapped_column(String)

    @classmethod
    def get_detail(cls, participant_id: str) -> "Participant | None":
        return db.session.get(cls, participant_id)
