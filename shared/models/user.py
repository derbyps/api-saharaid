from datetime import datetime

import uuid_extensions
from sqlalchemy import BINARY, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.configs.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id: Mapped[bytes] = mapped_column(
        BINARY(16),
        primary_key=True,
        default=lambda: uuid_extensions.uuid7(as_type="bytes"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
