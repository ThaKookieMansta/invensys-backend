"""
Accessories API Router.

This module defines the FastAPI routes for managing accessories, including:
    * Adding new accessories
    * Retrieving accessories by ID
    * Assigning accessories to allocations
    * (Optionally) updating and deleting accessories

Typical usage example:

    from apis.v1 import route_accessories
    api_router.include_router(route_accessories.router, prefix="", tags=["Accessories"])
"""

import uuid

from fastapi import status, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apis.v1.route_login import get_current_user
from db.models.is_users import User
from db.repository.accessory import repo_get_an_accessory, \
    repo_assign_accessory, repo_create_accessory, repo_get_all_accessories
from db.repository.user import repo_report_unauthorized_access
from db.sessions import get_db
from schemas.accessory import CreateAccessory, ShowAccessories

router = APIRouter()


@router.post("/add-accessory", response_model=ShowAccessories,
             status_code=status.HTTP_201_CREATED)
async def api_add_accessory(
        new_accessory: CreateAccessory, db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Create a New Accessory**

Creates a new accessory record in the system.

**Request Body:**
- `name` (str): The name of the accessory.
- `serial_number` (str): The unique serial number of the accessory.
- `assigned_to_allocation` (UUID, optional): The allocation ID this accessory is assigned to.

**Responses:**
- **201 Created:** Returns the details of the newly created accessory.
- **401 Unauthorized:** The user is not authorized to add an accessory.
- **422 Unprocessable Entity:** The request body failed validation.

    """

    if not admin.is_superuser:
        return await repo_report_unauthorized_access(
            task_logged="Create Accessory", table_name="is_accessory",
            admin=admin, db=db)

    return await repo_create_accessory(new_accessory, db, admin)


@router.get("/get-accessory", response_model=ShowAccessories,
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_accessory(
        id: uuid.UUID, db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Get Accessory by ID**

Fetches details of a specific accessory using its unique ID.

**Query Parameters:**
- `id` (UUID): The unique ID of the accessory to retrieve.

**Responses:**
- **202 Accepted:** Returns the accessory details.
- **401 Unauthorized:** The user is not authorized to view this resource.
- **422 Unprocessable Entity:** The provided ID is invalid.

    """

    return await repo_get_an_accessory(id, db, admin)


@router.get("/get-all-accessories", response_model=list[ShowAccessories],
            status_code=status.HTTP_202_ACCEPTED)
async def route_get_all_accessories(
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Get All Accessories**

    Retrieves a list of all accessories recorded in the system.

    This endpoint allows administrators to view all laptop-related accessories,
    such as chargers, bags, mice, or other peripherals that are tracked alongside
    laptop allocations.

    **Responses:**
    - **202 Accepted:** Returns a list of accessories available in the system.
    - **401 Unauthorized:** If the requester is not authenticated or lacks administrator privileges.

    **Returns:**
    A list of accessories, each including its identifying and descriptive details.

    **Authorization:**
    Requires administrator privileges.
    """

    return await repo_get_all_accessories(db, admin)


@router.put("/assign-accessory", response_model=ShowAccessories,
            status_code=status.HTTP_202_ACCEPTED)
async def api_assign_accessory(
        id: uuid.UUID, allocation_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Assign Accessory to Allocation**

Links an existing accessory to a specific laptop allocation.

**Request Body:**
- `accessory_id` (UUID): The unique ID of the accessory.
- `allocation_id` (UUID): The unique ID of the laptop allocation.

**Responses:**
- **202 Accepted:** Returns updated accessory details.
- **401 Unauthorized:** The user is not authorized to assign accessories.
- **422 Unprocessable Entity:** The request body failed validation.
    """

    return await repo_assign_accessory(accessory_id=id,
                                       allocation_id=allocation_id, db=db,
                                       admin=admin)
