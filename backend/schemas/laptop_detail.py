from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CreateLaptop(BaseModel):
    laptop_brand: str
    laptop_model: str
    serial_number: str
    laptop_name: str
    asset_tag: Optional[str]
    status_id: Optional[int]
    business_unit: str


class ShowLaptop(BaseModel):
    laptop_brand: str
    laptop_model: str
    serial_number:str
    laptop_name: str
    asset_tag: Optional[str]
    status_id: int
    business_unit: str
    created_at: datetime

    class config:
        orm_mode = True


class ShowLaptopCascaded(BaseModel):
    laptop_brand: str
    laptop_model: str
    serial_number:str
    laptop_name: str
    asset_tag: Optional[str]

    class config:
        orm_mode = True

class ModifyLaptop(BaseModel):
    pass

class ChangeLaptopStatus(BaseModel):
    status_id: int

