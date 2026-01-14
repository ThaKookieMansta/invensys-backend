import uuid

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ShowBusinessUnit(BaseModel):
    id: uuid.UUID
    unit_name: str
    is_active: bool
    created_at: datetime
    modified_at: Optional[datetime]

    class config:
        orm_mode = True


class ShowBusinessUnitName(BaseModel):
    unit_name: str

    class config:
        orm_mode = True


class CreateBusinessUnit(BaseModel):
    unit_name: str


class ModifyDepartment(BaseModel):
    pass
