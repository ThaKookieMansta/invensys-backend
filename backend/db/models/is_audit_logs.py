import uuid

from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from datetime import datetime


class AuditLogs(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("is_user.id"))
    action: Mapped[str] = mapped_column(String)
    table_name: Mapped[str] = mapped_column(String)
    record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    details: Mapped[str] = mapped_column(Text)

