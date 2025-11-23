from db.base import Base
from sqlalchemy.orm import mapped_column, Mapped, Relationship, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Integer, String, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
import uuid





class LaptopAllocation(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("is_user.id"))
    laptop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("is_laptopdetail.id"))
    allocation_date: Mapped[datetime] = mapped_column(DateTime)
    return_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    allocation_form: Mapped[str] = mapped_column(String, nullable=True)
    return_form: Mapped[str] = mapped_column(String, nullable=True)
    return_comment: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    allocated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("is_user.id"))
    allocation_condition: Mapped[str] = mapped_column(Text)
    returned_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("is_user.id"), nullable=True)
    reason_for_allocation: Mapped[str] = mapped_column(Text)
    condition_on_return: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="allocations",
        foreign_keys=[user_id],
        lazy="selectin"
    )
    laptop: Mapped["LaptopDetail"] = relationship(
        "LaptopDetail",
        back_populates="allocations",
        foreign_keys=[laptop_id],
        lazy="selectin"
    )


