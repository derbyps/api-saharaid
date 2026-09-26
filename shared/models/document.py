from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, func, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    participant_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("public.participants.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(Text, nullable=False)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False)


class DocumentDeletion(Base):
    __tablename__ = "document_deletions"
    __table_args__ = {"schema": "public"}

    document_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    participant_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("public.participants.id"), nullable=False)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
