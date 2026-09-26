from datetime import datetime
from uuid import UUID

import uuid_extensions
from sqlalchemy import BINARY, BigInteger, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "public"}

    id: Mapped[bytes] = mapped_column(
        BINARY(16),
        primary_key=True,
        default=lambda: uuid_extensions.uuid7(as_type="bytes"),
    )
    participant_id: Mapped[bytes] = mapped_column(BINARY)
    document_type: Mapped[str] = mapped_column(Text, nullable=False)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[UUID] = mapped_column(BINARY)


class DocumentDeletion(Base):
    __tablename__ = "document_deletions"
    __table_args__ = {"schema": "public"}

    document_id: Mapped[bytes] = mapped_column(BINARY)
    participant_id: Mapped[bytes] = mapped_column(BINARY)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
