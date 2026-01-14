from db.base import Base
from sqlalchemy.orm import Relationship, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Integer, String, DateTime, ForeignKey
from datetime import datetime
import uuid

from db.models.is_laptop_status import LaptopStatus
from db.models.is_repair_history import RepairHistory


class LaptopDetail(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    laptop_brand: Mapped[str] = mapped_column(String)
    laptop_model: Mapped[str] = mapped_column(String, nullable=False)
    serial_number: Mapped[str] = mapped_column(String, nullable=False,
                                               unique=True)
    laptop_name: Mapped[str] = mapped_column(String, nullable=False,
                                             unique=True)
    asset_tag: Mapped[str] = mapped_column(String)
    status_id: Mapped[int] = mapped_column(ForeignKey('is_laptopstatus.id'))
    business_unit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                        ForeignKey(
                                                            "is_businessunit.id"),
                                                        nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.now)

    allocations: Mapped[list["LaptopAllocation"]] = relationship(
        "LaptopAllocation",
        back_populates="laptop",
        lazy="selectin"
    )

    repairs: Mapped[list["RepairHistory"]] = relationship(
        "RepairHistory",
        back_populates="laptop",
        lazy="selectin"
    )

    status: Mapped["LaptopStatus"] = relationship(
        "LaptopStatus",
        back_populates="laptops",
        foreign_keys=[status_id],
        lazy="selectin"
    )
    business_unit = relationship("BusinessUnit", lazy="selectin")
