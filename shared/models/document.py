import uuid_extensions
from sqlalchemy import BigInteger, DateTime, String, func
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
    uploaded_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[str] = mapped_column(String)


class DocumentDeletion(Base):
    __tablename__ = "document_deletions"

    document_id: Mapped[str] = mapped_column(String)
    participant_id: Mapped[str] = mapped_column(String)
    s3_key: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
