import uuid

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from schemas.laptop_detail import ShowLaptopCascaded


class CreateRepairHistory(BaseModel):
    laptop_id: uuid.UUID
    repair_details: str
    date_fault_reported: datetime
    date_laptop_repaired: datetime
    cost_of_repair: float
    repair_vendor: str
    repaired_by: int
    warranty_covered: bool
    invoice_number: str


class ShowRepairHistory(BaseModel):
    laptop_id: uuid.UUID
    laptop: ShowLaptopCascaded
    repair_details: str
    date_fault_reported: datetime
    date_laptop_repaired: datetime
    cost_of_repair: float
    repair_vendor: str
    repaired_by: int
    warranty_covered: bool
    invoice_number: str


    class config:
        orm_mode = True

