from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.is_roles import Role
from schemas.role import CreateRole, ShowRole, ModifyRole
from datetime import datetime


async def repo_get_role(id: int, db: AsyncSession):
    result = await db.execute(select(Role).where(Role.id == id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such role exists"
        )
    return role