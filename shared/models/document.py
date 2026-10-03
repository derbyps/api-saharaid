import uuid_extensions
from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_extensions.uuid7()),
    )
    participant_id: Mapped[str] = mapped_column(String)
    document_type: Mapped[str] = mapped_column(String, nullable=False)
    s3_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_modified_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    uploaded_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(String)

    def __init__(
        self,
        participant_id: str,
        document_type: str,
        s3_key: str,
        original_filename: str,
        content_type: str,
        file_size: int,
        last_modified_at: str,
        uploaded_at: str,
        created_by: str,
    ):
        self.participant_id = participant_id
        self.document_type = document_type
        self.s3_key = s3_key
        self.original_filename = original_filename
        self.content_type = content_type
        self.file_size = file_size
        self.last_modified_at = last_modified_at
        self.uploaded_at = uploaded_at
        self.created_by = created_by


class DocumentDeletion(Base):
    __tablename__ = "document_deletions"

    document_id: Mapped[str] = mapped_column(String, primary_key=True)
    participant_id: Mapped[str] = mapped_column(String)
    s3_key: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)

    def __init__(
        self,
        document_id: str,
        participant_id: str,
        s3_key: str,
        created_at: str,
    ):
        self.document_id = document_id
        self.participant_id = participant_id
        self.s3_key = s3_key
        self.created_at = created_at
