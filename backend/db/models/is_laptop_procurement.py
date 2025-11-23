from db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Integer, String, DateTime, Float, ForeignKey
from datetime import datetime
import uuid


class LaptopProcurement(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    laptop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("is_laptopdetail.id"))
    purchase_date: Mapped[datetime] = mapped_column(DateTime)
    purchase_order: Mapped[str] = mapped_column(String)
    vendor: Mapped[str] = mapped_column(String)
    warranty_expiry: Mapped[datetime] = mapped_column(DateTime)
    cost: Mapped[float] = mapped_column(Float)
    purchase_order_file: Mapped[str] = mapped_column(String, nullable=True)

