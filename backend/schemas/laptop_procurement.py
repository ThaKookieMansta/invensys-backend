import uuid

from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class CreateLaptopProcurement(BaseModel):
    laptop_id: uuid.UUID
    purchase_date: datetime
    purchase_order: str
    vendor: str
    warranty_expiry: datetime
    cost: float


class ShowLaptopProcurement(BaseModel):
    laptop_id: uuid.UUID
    purchase_date: datetime
    purchase_order: str
    vendor: str
    warranty_expiry: datetime
    cost: float

    class config:
        orm_mode = True


class UploadPurchaseOrder(BaseModel):
    purchase_order_file: str