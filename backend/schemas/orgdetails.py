import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ShowOrganization(BaseModel):
    id: uuid.UUID
    organization_name: str
    street_address: Optional[str]
    po_box: Optional[str]
    created_at: datetime
    modified_at: Optional[datetime]

    class config:
        orm_mode = True


class AddOrganization(BaseModel):
    organization_name: str
    street_address: Optional[str]
    po_box: Optional[str]


class ModifyOrganization(BaseModel):
    organization_name: Optional[str]
    street_address: Optional[str]
    po_box: Optional[str]
