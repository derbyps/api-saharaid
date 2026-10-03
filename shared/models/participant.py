import uuid_extensions
from sqlalchemy import BigInteger, Boolean, Date, DateTime, String, text
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
    serial_number: Mapped[int] = mapped_column(BigInteger, unique=True)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    deleted_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    deleted_by: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(String)
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    updated_by: Mapped[str | None] = mapped_column(String)

    def __init__(
        self,
        name: str,
        identity_number: str,
        gender: str,
        phone_number: str,
        email: str,
        date_of_birth: str,
        religion: str,
        address: str,
        job_position: str,
        job_company: str,
        education: str,
        cr_number: str,
        tax_number: str,
        created_at: str,
        created_by: str,
        is_deleted: bool = False,
        updated_at: str | None = None,
        updated_by: str | None = None,
        deleted_at: str | None = None,
        deleted_by: str | None = None,
    ):
        self.name = name
        self.identity_number = identity_number
        self.gender = gender
        self.phone_number = phone_number
        self.email = email
        self.date_of_birth = date_of_birth
        self.religion = religion
        self.address = address
        self.job_position = job_position
        self.job_company = job_company
        self.education = education
        self.cr_number = cr_number
        self.tax_number = tax_number
        self.is_deleted = is_deleted
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by

    @classmethod
    def get_detail(cls, participant_id: str) -> "Participant | None":
        return db.session.get(cls, participant_id)
