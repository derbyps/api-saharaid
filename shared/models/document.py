import uuid_extensions
from sqlalchemy import Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    owner_id: Mapped[str] = mapped_column(String)
    owner_type: Mapped[str] = mapped_column(String)
    document_type: Mapped[str] = mapped_column(String)
    s3_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
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
        owner_id: str,
        owner_type: str,
        document_type: str,
        s3_key: str,
        created_at: str,
        created_by: str,
        is_deleted: bool = False,
        updated_at: str | None = None,
        updated_by: str | None = None,
        deleted_at: str | None = None,
        deleted_by: str | None = None,
    ):
        self.owner_id = owner_id
        self.owner_type = owner_type
        self.document_type = document_type
        self.s3_key = s3_key
        self.is_deleted = is_deleted
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by


class DocumentDeletion(Base):
    __tablename__ = "document_deletions"

    document_id: Mapped[str] = mapped_column(String, primary_key=True)
    participant_id: Mapped[str] = mapped_column(String)
    s3_key: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
