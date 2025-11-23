import uuid
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.is_repair_history import RepairHistory
from schemas.repair_history import CreateRepairHistory, ShowRepairHistory


async def repo_create_entry(entry: CreateRepairHistory, db: AsyncSession):
    new_entry = RepairHistory(
        laptop_id = entry.laptop_id,
        repair_details = entry.repair_details,
        date_fault_reported = entry.date_fault_reported,
        date_laptop_repaired = entry.date_laptop_repaired,
        cost_of_repair = entry.cost_of_repair,
        repair_vendor = entry.repair_vendor,
        repaired_by = entry.repaired_by,
        warranty_covered = entry.warranty_covered,
        invoice_number = entry.invoice_number
    )

    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry

async def repo_show_repairs(db: AsyncSession):
    result = await db.execute(select(RepairHistory))
    return result.scalars().all()


async def repo_show_an_entry(id: uuid.UUID, db: AsyncSession):
    result = await db.execute(select(RepairHistory).where(RepairHistory.id == id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="!!!ENTRY NOT FOUND!!!"
        )
    return entry

