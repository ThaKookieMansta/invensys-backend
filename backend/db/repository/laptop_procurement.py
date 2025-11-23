from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import timedelta, datetime
from typing import Optional
import uuid

from db.models.is_users import User
from db.models.is_laptop_procurement import LaptopProcurement
from db.models.is_audit_logs import AuditLogs
from db.models.is_laptop_details import LaptopDetail
from schemas.laptop_procurement import CreateLaptopProcurement, ShowLaptopProcurement
from core.minio_client import minio_client, BUCKET_NAME


async def repo_new_laptop_purchase(procurement: CreateLaptopProcurement, db: AsyncSession, admin: User):
    new_purchase = LaptopProcurement(
        laptop_id = procurement.laptop_id,
        purchase_date = procurement.purchase_date,
        purchase_order = procurement.purchase_order,
        vendor = procurement.vendor,
        warranty_expiry = procurement.warranty_expiry,
        cost = procurement.cost
    )

    db.add(new_purchase)

    laptop_search = await db.execute(select(LaptopDetail).where(LaptopDetail.id == procurement.laptop_id))
    laptop = laptop_search.scalar_one_or_none()

    new_audit_entry = AuditLogs(
        user_id = admin.id,
        action = "Added laptop to procurement table",
        table_name = "is_laptopprocurement",
        record_id = uuid.uuid4(),
        details = f"{admin.username}: Added procurement details of laptop({laptop.laptop_brand} {laptop.laptop_model} {laptop.serial_number}"
    )

    db.add(new_audit_entry)
    await db.commit()
    await db.refresh(new_purchase)
    await db.refresh(new_audit_entry)

    return new_purchase


async def repo_upload_purchase_order(record_id: uuid.UUID, db: AsyncSession, object_name:str, admin: User):
    record_search = await db.execute(select(LaptopProcurement).where(LaptopProcurement.id == record_id))
    record = record_search.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!! Record not found!!!"
        )

    record.purchase_order_file = object_name

    new_audit_entry = AuditLogs(
        user_id = admin.id,
        action = "File Upload",
        table_name = "is_laptopallocation",
        record_id = record.id,
        details = f"{admin.username}: Uploaded PO {record.purchase_order}"
    )

    db.add(new_audit_entry)

    await db.commit()
    await db.refresh(record)
    await db.refresh(new_audit_entry)
    return record

async def repo_download_PO(
        record_id: uuid.UUID,
        db: AsyncSession,
        admin: User
):
    record_search = await db.execute(select(LaptopProcurement).where(LaptopProcurement.id == record_id))
    record = record_search.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"!!! Recodr not found !!!"
        )
    if not record.purchase_order_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{record.id} does not have a PO attached to it."
        )

    url = minio_client.presigned_get_object(
        bucket_name=BUCKET_NAME,
        object_name=record.purchase_order_file,
        expires=timedelta(seconds=3600)
    )

    new_audit_entry = AuditLogs(
        user_id = admin.id,
        action = "File Download",
        table_name = "is_laptopprocurement",
        record_id = record.id,
        details = f"{admin.username}: Downloaded PO {record.purchase_order}"
    )

    db.add(new_audit_entry)
    await db.commit()
    await db.refresh(new_audit_entry)

    return {
        "url": url
    }

async def repo_quiet_search(record_id: uuid.UUID, db: AsyncSession, admin: User):
    record_search = await db.execute(
        select(LaptopProcurement).where(LaptopProcurement.id == record_id)
    )
    record = record_search.scalar_one_or_none()

    if not record:
        new_audit_log = AuditLogs(
            user_id = admin.id,
            action = "Record Search",
            table_name = "is_laptopprocuurement",
            record_id = record_id,
            details = f"‼️ Failed Record search ‼️"
        )
        db.add(new_audit_log)
        await db.commit()
        await db.refresh(new_audit_log)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="‼️Record does not exist‼️"
        )
    return True

async def repo_get_a_record(
        record_id: uuid.UUID,
        db: AsyncSession,
        admin: User
):
    record_search = await db.execute(
        select(LaptopProcurement).where(LaptopProcurement.id == record_id)
    )
    record = record_search.scalar_one_or_none()

    if not record:
        new_audit_log = AuditLogs(
            user_id = admin.id,
            action = "Record Search",
            table_name = "is_laptopprocuurement",
            record_id = record_id,
            details = f"‼️ Failed Record search ‼️"
        )
        db.add(new_audit_log)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="‼️The Record does not exist ‼️"
        )

    new_audit_log = AuditLogs(
        user_id=admin.id,
        action="Record Search",
        table_name="is_laptopprocuurement",
        record_id=record_id,
        details=f"{admin.username}: Selected a record {record_id}"
    )
    db.add(new_audit_log)
    await db.commit()
    await db.refresh(new_audit_log)
    return record

async def repo_get_records(
        db: AsyncSession,
        admin: User,
        purchase_order: str,
        purchase_date: datetime,
        vendor: str

):
    details = f"{admin.username} searched through the Procurement records:"

    query = (select(LaptopProcurement))
    if purchase_order:
        query = query.where(LaptopProcurement.purchase_order == purchase_order)
        details = f"{details} Purchase Order = {purchase_order}"
    if purchase_date:
        query = query.where(LaptopProcurement.purchase_date == purchase_date)
        details = f"{details} Date of Purchase = {purchase_date}"
    if vendor:
        query = query.where(LaptopProcurement.vendor == vendor)
        details = f"{details} Vendor = {vendor}"
    records_search = await db.execute(query)

    new_log = AuditLogs(
        user_id = admin.id,
        action = "Record Search",
        table_name = "is laptopprocurement",
        record_id = uuid.uuid4(),
        details = details
    )

    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)

    return records_search.scalars().all()

