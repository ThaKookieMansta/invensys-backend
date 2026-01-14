import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.logging_config import logger
from db.models.is_org_details import BusinessUnit
from db.models.is_users import User
from schemas.business_unit import CreateBusinessUnit


async def repo_new_business_unit(
        business_unit: CreateBusinessUnit, db: AsyncSession, admin: User,
):
    new_business_unit = BusinessUnit(
        unit_name=business_unit.unit_name.lower()
    )

    db.add(new_business_unit)
    logger.info(
        f"{admin.username}: Added Business Unit {business_unit.unit_name.title()}")
    await db.commit()
    await db.refresh(new_business_unit)
    return new_business_unit


async def repo_get_business_unit(id: uuid.UUID, db: AsyncSession, admin: User):
    result = await db.execute(
        select(BusinessUnit).where(BusinessUnit.id == id))
    business_unit = result.scalar_one_or_none()
    if not business_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!Business Unit NOT FOUND!!!⚠️"
        )
    logger.info(f"{admin.username}: searched for Business Unit {id}")

    return business_unit


async def repo_get_business_units(
        db: AsyncSession, admin: User, business_unit: Optional[str] = None,
):
    details = f"{admin.username} searched through Business Units:"

    query = (select(BusinessUnit))
    if business_unit is not None:
        query = query.where(BusinessUnit.unit_name == business_unit)
        details = f"{details} Business Unit = {business_unit.title()}"

    result = await db.execute(query)

    logger.info(details)

    return result.scalars().all()


async def repo_update_business_unit(
        id: uuid.UUID, db: AsyncSession, admin: User,
        new_unit_name: CreateBusinessUnit,
):
    result = await db.execute(
        select(BusinessUnit).where(BusinessUnit.id == id))
    bu_result = result.scalar_one_or_none()
    if not bu_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!Business Unit NOT FOUND!!!⚠️"
        )
    bu_result.department_name = new_unit_name.unit_name
    bu_result.modified_at = datetime.now()

    logger.info(
        f"{admin.username} Updated the department name {bu_result.unit_name} into {new_unit_name.unit_name}")
    await db.commit()
    await db.refresh(bu_result)
    return bu_result


async def repo_delete_business_unit(
        id: uuid.UUID, db: AsyncSession, admin: User,
):

    result = await db.execute(
        select(BusinessUnit).where(BusinessUnit.id == id))
    bu_result = result.scalar_one_or_none()
    if not bu_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!Business Unit NOT FOUND!!!⚠️"
        )

    logger.info(
        f"{admin.username} Deleted Business Unit {bu_result.unit_name}")
    await db.delete(bu_result)
    await db.commit()
    return {
        "msg": f"Deleted Business Unit '{bu_result.unit_name}'"
    }
