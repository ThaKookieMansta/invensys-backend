import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.logging_config import logger
from db.models.is_org_details import Department
from db.models.is_users import User
from schemas.department import CreateDepartment


async def repo_new_department(
        department: CreateDepartment, db: AsyncSession, admin: User,
):
    new_department = Department(
        department_name=department.department_name.lower(),
        created_at=datetime.now()
    )

    db.add(new_department)
    logger.info(
        f"{admin.username}: Added Department {department.department_name.title()}")
    await db.commit()
    await db.refresh(new_department)
    return new_department


async def repo_get_department(id: uuid.UUID, db: AsyncSession, admin: User):
    result = await db.execute(select(Department).where(Department.id == id))
    department = result.scalar_one_or_none()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!DEPARTMENT NOT FOUND!!!⚠️"
        )
    logger.info(f"{admin.username}: searched for department {department.id}")

    return department


async def repo_get_departments(
        db: AsyncSession, admin: User, department: Optional[str] = None,
):
    details = f"{admin.username} searched through departments:"

    query = (select(Department))
    if department is not None:
        query = query.where(Department.department_name == department)
        details = f"{details} department = {department.title()}"

    result = await db.execute(query)

    logger.info(details)

    return result.scalars().all()


async def repo_update_department(
        id: uuid.UUID, db: AsyncSession, admin: User,
        new_department_name: CreateDepartment,
):
    result = await db.execute(select(Department).where(Department.id == id))
    department_result = result.scalar_one_or_none()
    if not department_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!DEPARTMENT NOT FOUND!!!⚠️"
        )
    department_result.department_name = new_department_name.department_name
    department_result.modified_at = datetime.now()

    logger.info(
        f"{admin.username} Updated the department name {department_result.department_name} into {new_department_name.department_name}")
    await db.commit()
    await db.refresh(department_result)
    return department_result


async def repo_delete_department(
        id: uuid.UUID, db: AsyncSession, admin: User,
):

    result = await db.execute(select(Department).where(Department.id == id))
    department_result = result.scalar_one_or_none()
    if not department_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!DEPARTMENT NOT FOUND!!!⚠️"
        )

    logger.info(
        f"{admin.username} Deleted department {department_result.department_name}")
    await db.delete(department_result)
    await db.commit()
    return {
        "msg": f"Deleted Department '{department_result.department_name}'"
    }
