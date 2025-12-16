import uuid

from pydantic import BaseModel
from typing import Optional


class CreateAccessory(BaseModel):
    name: str
    serial_number: Optional[str]
    assigned_to_allocation: Optional[uuid.UUID]


class ShowAccessories(BaseModel):
    id: uuid.UUID
    name: str
    serial_number: str
    assigned_to_allocation: Optional[uuid.UUID]

    class config:
        orm_mode = True


class ModifyAccessoryAllocation(BaseModel):
    assigned_to_allocation: uuid.UUID
