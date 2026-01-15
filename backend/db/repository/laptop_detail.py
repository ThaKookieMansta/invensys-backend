import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.logging_config import logger
from db.models.is_laptop_details import LaptopDetail
from db.models.is_laptop_status import LaptopStatus
from db.models.is_users import User
from schemas.laptop_detail import CreateLaptop, ChangeLaptopStatus


async def repo_new_laptop(laptop: CreateLaptop, db: AsyncSession, admin: User):
    new_laptop = LaptopDetail(
        laptop_brand=laptop.laptop_brand,
        laptop_model=laptop.laptop_model,
        serial_number=laptop.serial_number,
        laptop_name=laptop.laptop_name.lower(),
        asset_tag=laptop.asset_tag,
        status_id=laptop.status_id,
        business_unit_id=laptop.business_unit_id,

    )

    db.add(new_laptop)

    detail_txt = f"{laptop.laptop_brand} {laptop.laptop_model} {laptop.serial_number}"

    logger.info(f"{admin.username}: Added laptop {detail_txt}")

    await db.commit()
    await db.refresh(new_laptop)
    return new_laptop


async def repo_get_a_laptop(id: uuid.UUID, db: AsyncSession, admin: User):
    result = await db.execute(
        select(LaptopDetail).where(LaptopDetail.id == id))
    laptop = result.scalar_one_or_none()
    if not laptop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!LAPTOP NOT FOUND!!!⚠️"
        )

    logger.info(f"{admin.username}: Searched for laptop {laptop.id}")

    return laptop


async def repo_get_laptops(
        db: AsyncSession,
        admin: User,
        laptop_status: Optional[str] = None,
        business_unit_id: Optional[str] = None,
):
    details = f"{admin.username} searched through laptops:"

    query = (select(LaptopDetail).options(selectinload(LaptopDetail.status)))
    if laptop_status is not None:
        query = query.join(LaptopDetail.status).where(
            LaptopStatus.status_name == laptop_status)
        log_laptop_status = laptop_status.value
        details = f"{details} status = {log_laptop_status}"
    if business_unit_id is not None:
        query = query.where(LaptopDetail.business_unit_id == business_unit_id)
        details = f"{details} business unit = {business_unit_id}"
    result = await db.execute(query)

    logger.info(details)

    return result.scalars().all()


async def repo_modify_laptop_status(
        id: uuid.UUID, laptop_status: ChangeLaptopStatus, db: AsyncSession,
        admin: User,
):
    result = await db.execute(
        select(LaptopDetail).where(LaptopDetail.id == id))
    laptop = result.scalar_one_or_none()
    if not laptop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!LAPTOP NOT FOUND!!!⚠️",
        )
    laptop.status_id = laptop_status.status_id
    await db.commit()
    await db.refresh(laptop)

    logger.info(
        f"{admin.username} changed the laptop status for laptop {laptop.laptop_brand} {laptop.laptop_model} {laptop.serial_number}")

    return laptop


async def repo_delete_a_laptop(id: uuid.UUID, db: AsyncSession, admin: User):
    result = await db.execute(
        select(LaptopDetail).where(LaptopDetail.id == id))
    laptop = result.scalar_one_or_none()
    if not laptop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!LAPTOP NOT FOUND!!!⚠️",
        )
    laptop_brand = laptop.laptop_brand
    laptop_model = laptop.laptop_model
    serial_number = laptop.serial_number

    await db.delete(laptop)
    await db.commit()
    logger.info(
        f"{admin.username} deleted laptop {laptop_brand} - {laptop_model} - {serial_number}")
    return {
        "Message": f"{laptop_brand} {laptop_model} with the serial number\
{serial_number} has been deleted"
    }
