import uuid

from db.base import Base
from sqlalchemy.orm import Relationship, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from db.models.is_laptop_allocation import LaptopAllocation


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    email_address: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    business_unit: Mapped[str] = mapped_column(String, nullable=True)
    department: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    modified_at: Mapped[str] = mapped_column(DateTime, nullable=True)

    allocations: Mapped[list["LaptopAllocation"]] = relationship(
        "LaptopAllocation",
        back_populates="user",
        foreign_keys=[LaptopAllocation.user_id],
        lazy="selectin",
        cascade="all, delete-orphan"
    )

