import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging_config import logger
from db.models.is_org_details import OrganizationDetails
from db.models.is_users import User
from schemas.orgdetails import AddOrganization, ShowOrganization, \
    ModifyOrganization


async def repo_add_organization(
        organization: AddOrganization,
        db: AsyncSession,
        admin: User,
):
    new_organization = OrganizationDetails(
        organization_name=organization.organization_name,
        street_address=organization.street_address,
        po_box=organization.po_box
    )

    db.add(new_organization)

    logger.info(
        f"The Organization {organization.organization_name} was created")

    await db.commit()
    await db.refresh(new_organization)
    return new_organization


async def repo_update_organization(
        id: uuid.UUID,
        updated_organization: ModifyOrganization,
        db: AsyncSession,
        admin: User,
):
    result = await db.execute(
        select(OrganizationDetails).where(OrganizationDetails.id == id))
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"That Organization does not exist"
        )
    update_data = updated_organization.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    organization.modified_at = datetime.now()

    logger.info(f"{admin.username} updated organization details")

    await db.commit()
    await db.refresh(organization)
    return organization


async def repo_get_organization_details(
        id: uuid.UUID,
        db: AsyncSession,
        admin: User,
):
    result = await db.execute(
        select(OrganizationDetails).where(OrganizationDetails.id == id))
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"That Organization does not exist"
        )

    logger.info(f"{admin.username} looked up Organization details")


async def repo_list_organizations(
        db: AsyncSession,
        admin: User,
):
    result = await db.execute(select(OrganizationDetails))
    logger.info(f"{admin.username} searched Organizations")

    return result.scalars().all()


async def repo_get_organization_name(
        db: AsyncSession,
        admin: User,
):
    result = await db.execute(select(OrganizationDetails))
    # logger.info(f"{admin.username} searched Organizations")

    org = result.scalars().first().organization_name
    return org
