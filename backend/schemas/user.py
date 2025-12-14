import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from schemas.laptop_allocation import ShowAllocationsNested


class ShowUser(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    username: str
    email_address: EmailStr
    is_active: bool
    is_superuser: bool
    business_unit: Optional[str]
    department: Optional[str]
    created_at: datetime
    modified_at: Optional[datetime]
    allocations: List[ShowAllocationsNested] = []

    class config:
        orm_mode = True


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email_address: EmailStr
    password_hash: Optional[str] = Field(None)
    business_unit: str
    department: str

    @field_validator("password_hash")
    def check_password_length(cls, v):
        if v is not None and v != "" and len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class ModifyUser(BaseModel):
    pass


class ChangePassword(BaseModel):
    current_password: Optional[str] = Field(None)
    new_password: str = Field(..., min_length=8)
