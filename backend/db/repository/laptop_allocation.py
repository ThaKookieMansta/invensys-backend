import uuid
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.form_pdf_generator import generate_allocation_form
from core.logging_config import logger
from core.minio_client import minio_client, BUCKET_NAME
from db.models.is_laptop_allocation import LaptopAllocation
from db.models.is_laptop_details import LaptopDetail
from db.models.is_laptop_status import LaptopStatus
from db.models.is_users import User
from schemas.laptop_allocation import CreateAllocation, CreateReturn


async def repo_create_allocation(
        allocation: CreateAllocation, db: AsyncSession, allocator_id: int,
):
    new_allocation = LaptopAllocation(
        user_id=allocation.user_id,
        laptop_id=allocation.laptop_id,
        allocation_date=allocation.allocation_date,
        allocated_by=allocator_id,
        allocation_condition=allocation.allocation_condition,
        reason_for_allocation=allocation.reason_for_allocation

    )

    laptop_id = allocation.laptop_id

    db.add(new_allocation)

    result = await db.execute(
        select(LaptopDetail).where(LaptopDetail.id == laptop_id))
    laptop = result.scalar_one_or_none()
    status_result = await db.execute(
        select(LaptopStatus).where(LaptopStatus.status_name == "Allocated"))
    status_we_want = status_result.scalar_one_or_none()
    laptop.status_id = status_we_want.id

    allocator_result = await db.execute(
        select(User).where(User.id == allocator_id))
    allocator_details = allocator_result.scalar_one_or_none()
    allocated_user_result = await db.execute(
        select(User).where(User.id == allocation.user_id))
    allocated_user = allocated_user_result.scalar_one_or_none()

    await db.commit()
    await db.refresh(laptop)
    await db.refresh(new_allocation)

    logger.info(
        f"{allocator_details.username}: Allocated the laptop "
        f"({laptop.laptop_brand} {laptop.laptop_model} {laptop.serial_number} "
        f"{laptop.laptop_name}) to {allocated_user.username}")

    return new_allocation


async def repo_show_all_allocations(
        db: AsyncSession,
        admin: User,
        is_active: Optional[bool] = None,
        username: Optional[str] = None,
        serial_number: Optional[str] = None,
):
    details = f"{admin.username} searched through laptop allocations:"

    query = (
        select(LaptopAllocation).options(selectinload(LaptopAllocation.user),
                                         selectinload(
                                             LaptopAllocation.laptop)))
    if is_active is not None:
        query = query.where(LaptopAllocation.is_active == is_active)
        details = f"{details} is_active = {is_active}"
    if username:
        query = query.join(LaptopAllocation.user).where(
            User.username == username)
        details = f"{details} username = {username}"
    if serial_number:
        query = query.join(LaptopAllocation.laptop).where(
            LaptopDetail.serial_number == serial_number)
        details = f"{details} serial number = {serial_number}"
    result = await db.execute(query)

    logger.info(details)

    return result.scalars().all()


async def repo_show_an_allocation(
        id: uuid.UUID, db: AsyncSession, admin: User,
):
    result = await db.execute(
        select(LaptopAllocation).where(LaptopAllocation.id == id))
    alloc = result.scalar_one_or_none()
    if not alloc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!!ALLOCATION NOT FOUND!!!",
        )

    laptop_result = await db.execute(
        select(LaptopDetail).where(LaptopDetail.id == alloc.laptop_id))
    laptop = laptop_result.scalar_one_or_none()

    logger.info(f"{admin.username}: Searched allocation id {alloc.id}. "
                f"Allocation for {laptop.laptop_brand} {laptop.laptop_model} "
                f"with serial number {laptop.serial_number}")
    return alloc


async def repo_return_laptop(
        id: uuid.UUID, returned_laptop: CreateReturn, db: AsyncSession,
        allocator_id: int,
):
    result = await db.execute(
        select(LaptopAllocation).where(LaptopAllocation.id == id))
    alloc = result.scalar_one_or_none()

    if not alloc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!!Allocation not found!!!"
        )

    alloc.return_date = returned_laptop.return_date
    alloc.return_comment = returned_laptop.return_comment
    alloc.returned_by = allocator_id
    alloc.condition_on_return = returned_laptop.condition_on_return
    alloc.is_active = False

    laptop_result = await db.execute(
        select(LaptopDetail).where(LaptopDetail.id == alloc.laptop_id))
    laptop = laptop_result.scalar_one_or_none()
    status_result = await db.execute(
        select(LaptopStatus).where(LaptopStatus.status_name == "Available"))
    status_we_want = status_result.scalar_one_or_none()
    laptop.status_id = status_we_want.id
    allocator_result = await db.execute(
        select(User).where(User.id == allocator_id))
    allocator_details = allocator_result.scalar_one_or_none()
    allocated_user_result = await db.execute(
        select(User).where(User.id == alloc.user_id))
    allocated_user = allocated_user_result.scalar_one_or_none()

    logger.info(
        f"{allocator_details.username}: Returned the laptop ({laptop.laptop_brand} {laptop.laptop_model} {laptop.serial_number} {laptop.laptop_name} to the system from {allocated_user.username}")

    await db.commit()
    await db.refresh(alloc)
    await db.refresh(laptop)
    return alloc


async def repo_upload_form(
        id: uuid.UUID, db: AsyncSession, object_name: str, admin: User,
):
    result = await db.execute(
        select(LaptopAllocation).where(LaptopAllocation.id == id))
    allocation = result.scalar_one_or_none()

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!!Allocation not found!!!"
        )

    allocation.allocation_form = object_name

    logger.info(f"{admin.username}: Uploaded allocation form for"
                f" allocation - {allocation.id}")

    await db.commit()
    await db.refresh(allocation)
    return allocation


async def repo_download_form(id: uuid.UUID, db: AsyncSession, admin: User):
    result = await db.execute(
        select(LaptopAllocation).where(LaptopAllocation.id == id))
    allocation = result.scalar_one_or_none()

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!!Allocation not found!!!"
        )

    if not allocation.allocation_form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!!Document not found!!!"
        )

    url = minio_client.presigned_get_object(
        BUCKET_NAME,
        allocation.allocation_form,
        expires=timedelta(seconds=3600)
    )

    logger.info(f"{admin.username}: Downloaded allocation form for"
                f" allocation - {allocation.id}")

    return {
        "url": url
    }


async def repo_upload_return_form(
        id: uuid.UUID, db: AsyncSession, object_name: str, admin: User,
):
    result = await db.execute(
        select(LaptopAllocation).where(LaptopAllocation.id == id))
    allocation = result.scalar_one_or_none()

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!! Allocation Not Found !!!"
        )

    if allocation.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This laptop is still in use. Return it in the system before uploading a return form"
        )

    allocation.return_form = object_name

    logger.info(f"{admin.username}: Uploaded Return form for"
                f" allocation - {allocation.id}")

    await db.commit()
    await db.refresh(allocation)
    return allocation


async def repo_download_return_form(
        id: uuid.UUID, db: AsyncSession, admin: User,
):
    result = await db.execute(
        select(LaptopAllocation).where(LaptopAllocation.id == id))
    allocation = result.scalar_one_or_none()

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!! Allocation Not Found !!!"
        )

    if not allocation.return_form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!! Document not found!!!"
        )

    url = minio_client.presigned_get_object(
        bucket_name=BUCKET_NAME,
        object_name=allocation.return_form,
        expires=timedelta(seconds=3600)
    )

    logger.info(f"{admin.username}: Downloaded Return form for"
                f" allocation - {allocation.id}")

    return {
        "url": url
    }


# ############################################################################################
# --------------------------------- The code below is not final ------------------------------
# ############################################################################################

async def repo_create_allocation_form(
        allocation, org_config, db: AsyncSession,
):
    allocation_data = {
        "user": {
            "first_name": allocation.user.first_name,
            "last_name": allocation.user.last_name,
            "username": allocation.user.username,
        },
        "laptop": {
            "brand": allocation.laptop.laptop_brand,
            "model": allocation.laptop.laptop_model,
            "asset_tag": allocation.laptop.asset_tag,
            "serial_number": allocation.laptop.serial_number,
        },
        "allocation_date": str(allocation.allocation_date),
        "return_date": str(
            allocation.return_date) if allocation.return_date else None,
        "allocation_condition": allocation.allocation_condition,
        "reason_for_allocation": allocation.reason_for_allocation,
    }

    pdf_bytes = generate_allocation_form(allocation_data, org_config)

    user_result = await db.execute(
        select(User).where(User.id == allocation.allocated_by))
    user = user_result.scalar_one_or_none()

    logger.info(
        f"{user.username}: Generated allocation form for allocation {allocation.id}")

    return pdf_bytes


async def repo_create_return_form(allocation, org_config, db: AsyncSession):
    allocation_data = {
        "user": {
            "first_name": allocation.user.first_name,
            "last_name": allocation.user.last_name,
            "username": allocation.user.username,
        },
        "laptop": {
            "brand": allocation.laptop.laptop_brand,
            "model": allocation.laptop.laptop_model,
            "asset_tag": allocation.laptop.asset_tag,
            "serial_number": allocation.laptop.serial_number,
        },
        "return_date": str(allocation.return_date),
        "return_comment": allocation.return_comment,
        "condition_on_return": allocation.condition_on_return,
    }

    if not allocation.allocation_form:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot generate return form before allocation Form"
        )

    pdf_bytes = generate_allocation_form(allocation_data, org_config)

    user_result = await db.execute(
        select(User).where(User.id == allocation.returned_by))
    user = user_result.scalar_one_or_none()

    logger.info(
        f"{user.username}: Generated return form for allocation {allocation.id}")

    return pdf_bytes

