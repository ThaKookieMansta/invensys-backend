from datetime import datetime

from db.base import Base
from sqlalchemy.orm import mapped_column, Mapped, Relationship, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Integer, String, Boolean, DateTime
import uuid


class BusinessUnit(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    unit_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Department(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    department_name: Mapped[str] = mapped_column(String, nullable=True,
                                                 unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class OrganizationDetails(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                          primary_key=True,
                                          index=True,
                                          default=uuid.uuid4)
    organization_name: Mapped[str] = mapped_column(String, unique=True)
    street_address: Mapped[str] = mapped_column(String, nullable=True)
    po_box: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
