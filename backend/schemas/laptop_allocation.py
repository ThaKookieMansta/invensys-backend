import uuid

from pydantic import BaseModel, field_validator, field_serializer
from typing import Optional, List
from datetime import datetime

from schemas.laptop_detail import ShowLaptopCascaded


class CreateAllocation(BaseModel):
    user_id: uuid.UUID
    laptop_id: uuid.UUID
    allocation_date: datetime
    allocation_condition: str
    reason_for_allocation: str


class ShowAllocations(BaseModel):
    user_id: uuid.UUID
    laptop_id: uuid.UUID
    laptop: ShowLaptopCascaded
    allocation_date: datetime
    allocation_form: Optional[str]
    reason_for_allocation: str
    allocation_condition: str
    is_active: bool
    return_date: Optional[datetime]
    returned_by: Optional[uuid.UUID]
    return_comment: Optional[str]
    condition_on_return: Optional[str]
    return_form: Optional[str]


    class config:
        orm_mode = True



class ShowAllocationsNested(BaseModel):
    allocation_date: datetime
    allocation_condition: str
    reason_for_allocation:str
    is_active: bool
    return_date: Optional[datetime]



class ModifyAllocation(BaseModel):
    pass

class CreateReturn(BaseModel):
    return_date: datetime
    return_comment: str
    condition_on_return: str

class UploadAllocationForm(BaseModel):
    allocation_form: str

class UploadReturnForm(BaseModel):
    return_form: str
