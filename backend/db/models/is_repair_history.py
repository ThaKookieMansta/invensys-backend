from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, Relationship, relationship
from sqlalchemy import Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from db.base import Base
from datetime import datetime
import uuid


class RepairHistory(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    laptop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("is_laptopdetail.id"))
    repair_details: Mapped[str] = mapped_column(Text)
    date_fault_reported: Mapped[datetime] = mapped_column(DateTime())
    date_laptop_repaired: Mapped[datetime] = mapped_column(DateTime())
    cost_of_repair: Mapped[float] = mapped_column(Float)
    repair_vendor: Mapped[str] = mapped_column(String)
    repaired_by: Mapped[int] = mapped_column(ForeignKey("is_user.id"))
    warranty_covered: Mapped[bool] = mapped_column(Boolean)
    invoice_number: Mapped[str] = mapped_column(String)

    laptop: Mapped["LaptopDetail"] = relationship(
        "LaptopDetail",
        back_populates="repairs",
        foreign_keys=[laptop_id],
        lazy="selectin"
    )

