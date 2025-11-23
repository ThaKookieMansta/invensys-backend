from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Accessories(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    serial_number: Mapped[str] = mapped_column(String, unique=True)
    assigned_to_allocation: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("is_laptopallocation.id"), nullable=True)

