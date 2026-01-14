import uuid

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ShowDepartment(BaseModel):
    id: uuid.UUID
    department_name: str
    is_active: bool
    created_at: datetime
    modified_at: Optional[datetime]

    class config:
        orm_mode = True


class ShowDepartmentName(BaseModel):
    department_name: str

    class config:
        orm_mode = True


class CreateDepartment(BaseModel):
    department_name: str


class ModifyDepartment(BaseModel):
    pass
