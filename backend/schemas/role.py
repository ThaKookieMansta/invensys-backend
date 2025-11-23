from pydantic import BaseModel
from typing import Optional


class CreateRole(BaseModel):
    name: str


class ShowRole(BaseModel):
    name: str

    class config:
        orm_mode = True

class ModifyRole(BaseModel):
    pass

