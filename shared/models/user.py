from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Text, func, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
