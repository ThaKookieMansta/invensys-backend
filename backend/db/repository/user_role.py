from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.is_users import User
from db.models.is_user_roles import UserRole
from schemas.user_role import CreateUserRole, ShowUserRole, ModifyUser
from db.repository.user import repo_get_a_user
from db.repository.role import repo_get_role
from datetime import datetime


async def repo_assign_role(user_id: int, role_id: int, db: AsyncSession):
    user = await repo_get_a_user(id=user_id, db=db)
    role = await repo_get_role(id=role_id, db=db)
    new_assignment = UserRole(
        user_id = user.id,
        role_id = role.id
    )

async def repo_show_roles(db: AsyncSession):
    result = await db.execute(select(UserRole))
    return result.scalars().all()


