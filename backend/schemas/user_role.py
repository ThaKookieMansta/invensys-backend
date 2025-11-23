from pydantic import BaseModel
from typing import Optional

class CreateUserRole(BaseModel):
    user_id: int
    role_id: int


class ShowUserRole(BaseModel):
    user_id: int
    role_id: int


    class config:
        orm_mode = True


class ModifyUser(BaseModel):
    pass

