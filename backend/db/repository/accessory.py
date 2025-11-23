from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from schemas.accessory import CreateAccessory
from db.models.is_accessories import Accessories
from db.models.is_users import User
from core.logging_config import logger

async def repo_create_accessory(accessory: CreateAccessory, db: AsyncSession, admin: User):
    new_accessory = Accessories(
        name = accessory.name,
        serial_number = accessory.serial_number
    )

    logger.info(f"{admin.username} created accessory (id={new_accessory.id} name={new_accessory.name})")

    db.add(new_accessory)
    await db.commit()
    await db.refresh(new_accessory)
    return new_accessory

async def repo_assign_accessory(accessory_id: uuid.UUID, allocation_id: uuid.UUID, db: AsyncSession, admin: User):
    result = await db.execute(select(Accessories).where(Accessories.id == accessory_id))
    accessory = result.scalar_one_or_none()
    if not accessory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!ACCESORRY NOT FOUND!!!⚠️",
        )
    accessory.assigned_to_allocation = allocation_id

    logger.info(f"{admin.username} assigned accessory (id={accessory.id} name={accessory.name}) to {allocation_id}")

    await db.commit()
    await db.refresh(accessory)
    return accessory

async def repo_get_an_accessory(id: uuid.UUID, db: AsyncSession, admin: User):
    result = await db.execute(select(Accessories).where(Accessories.id == id))
    accessory = result.scalar_one_or_none()
    if not accessory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!ACCESORRY NOT FOUND!!!⚠️",
        )

    logger.info(f"{admin.username} Searched accessory (id={accessory.id} name={accessory.name})")

    return accessory


async def repo_get_all_accessories(db: AsyncSession, admin: User):
    result = await db.execute(select(Accessories))

    logger.info(f"{admin.username} Searched though all accessories")

    return result.scalars().all()

async def repo_return_an_accessory(id: uuid.UUID, db: AsyncSession, admin: User):
    result = await db.execute(select(Accessories).where(Accessories.id == id))
    accessory = result.scalar_one_or_none()
    if not accessory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="⚠️!!!ACCESORRY NOT FOUND!!!⚠️",
        )
    accessory.assigned_to_allocation = None

    logger.info(f"{admin.username} Returnd accessory (id={accessory.id} name={accessory.name})")

    await db.commit()
    await db.refresh(accessory)
    return accessory

