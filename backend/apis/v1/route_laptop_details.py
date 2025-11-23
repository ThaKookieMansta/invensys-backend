"""
Laptop Details Routes
---------------------

This module defines the API endpoints for managing laptop records in the system.
It provides functionality to add, update, retrieve, and delete laptop entries.
All routes require authentication, and certain actions are restricted to administrators.

Endpoints Overview
==================

**POST**
- **/add-laptop**
  Create and register a new laptop in the system.

**PUT**
- **/change_laptop_status**
  Update the operational or allocation status of a specific laptop.

**GET**
- **/get-a-laptop**
  Retrieve detailed information about a specific laptop by its ID.

- **/get-all-laptops**
  Retrieve a filtered list of all laptops. Filters can include status or business unit.

**DELETE**
- **/delete-a-laptop**
  Permanently remove a laptop record from the database.

Notes
=====
- All routes require authentication via the `get_current_user` dependency.
- Only users with administrative privileges can create, modify, or delete laptop records.
- Laptop statuses are managed using the `LaptopStatus` enum to ensure consistency.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apis.v1.route_login import get_current_user
from db.models.is_users import User
from db.repository.laptop_detail import repo_get_a_laptop, repo_new_laptop, \
    repo_get_laptops, repo_delete_a_laptop, repo_modify_laptop_status
from db.sessions import get_db
from enums.laptop_status import LaptopStatus
from schemas.laptop_detail import CreateLaptop, ShowLaptop, ChangeLaptopStatus

router = APIRouter()


@router.post("/add-laptop", response_model=ShowLaptop,
             status_code=status.HTTP_202_ACCEPTED)
async def api_new_laptop(
        laptop: CreateLaptop, db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Add a new laptop to the system. (Admin only)**

    This endpoint allows an administrator to register a new laptop in the system.
    It captures key device details such as model, serial number, and specifications,
    and stores them in the database.

    **Args:**
    - **laptop (CreateLaptop):** The laptop data payload containing device details.
    - **db (AsyncSession):** The asynchronous database session.
    - **admin (User):** The currently authenticated administrator performing the action.

    **Returns:**
    - **ShowLaptop:** The details of the newly added laptop.

    **Raises:**
    - **401 Unauthorized:** If the user is not authenticated or lacks admin privileges.
    - **422 Unprocessable Entity:** If the provided laptop details fail validation.
    """

    return await repo_new_laptop(laptop, db, admin)


@router.get("/get-a-laptop", response_model=ShowLaptop,
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_a_laptop(
        id: uuid.UUID, db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
        **Retrieve details of a specific laptop. (Admin only)**

        This endpoint allows an administrator to fetch detailed information about
        a single laptop using its unique identifier (UUID). It is typically used
        to verify registration data or inspect allocation readiness.

        **Args:**
        - **id (uuid.UUID):** The unique identifier of the laptop.
        - **db (AsyncSession):** The asynchronous database session.
        - **admin (User):** The authenticated administrator performing the action.

        **Returns:**
        - **ShowLaptop:** The laptop record corresponding to the provided ID.

        **Raises:**
        - **401 Unauthorized:** If the user is not authenticated or lacks admin privileges.
        - **404 Not Found:** If the laptop with the given ID does not exist.
        - **422 Unprocessable Entity:** If the provided ID is invalid.
        """
    return await repo_get_a_laptop(id, db, admin)


@router.get("/get-all-laptops", response_model=list[ShowLaptop],
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_all_laptops(
        laptop_status: Optional[LaptopStatus] = Query(default="Available",
                                                      description="Filter by Laptop status"),
        business_unit: Optional[str] = Query(None,
                                             description="Filter by Business Unit"),
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
        **Retrieve a list of all laptops in the system. (Admin only)**

        This endpoint allows administrators to view all registered laptops, with optional
        filters by **status** and **business unit**. It provides an overview of available,
        allocated, or decommissioned devices for easier inventory management.

        **Args:**
        - **laptop_status (Optional[LaptopStatus]):** Filter laptops by their current status (e.g., *Available*, *Allocated*, *Returned*). Defaults to `"Available"`.
        - **business_unit (Optional[str]):** Filter laptops by business unit name.
        - **db (AsyncSession):** The asynchronous database session.
        - **admin (User):** The authenticated administrator performing the action.

        **Returns:**
        - **list[ShowLaptop]:** A list of laptop records matching the applied filters.

        **Raises:**
        - **401 Unauthorized:** If the user is not authenticated or lacks admin privileges.
        - **422 Unprocessable Entity:** If filter parameters are invalid.
        """
    return await repo_get_laptops(db, admin, laptop_status, business_unit)


@router.put("/change_laptop_status", response_model=ShowLaptop,
            status_code=status.HTTP_202_ACCEPTED)
async def api_change_laptop_status(
        id: uuid.UUID, laptop_status: ChangeLaptopStatus,
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Change the status of a specific laptop. (Admin only)**

    This endpoint allows administrators to update the operational status of a laptop.
    It is typically used to mark laptops as *Available*, *Allocated*, *Decommissioned*, or
    any other valid status defined in the system.

    **Args:**
    - **id (uuid.UUID):** The unique identifier of the laptop to be updated.
    - **laptop_status (ChangeLaptopStatus):** The new status payload specifying the desired laptop state.
    - **db (AsyncSession):** The asynchronous database session.
    - **admin (User):** The authenticated administrator performing the update.

    **Returns:**
    - **ShowLaptop:** The updated laptop record with its new status.

    **Raises:**
    - **401 Unauthorized:** If the user is not authenticated or lacks admin privileges.
    - **404 Not Found:** If no laptop exists with the provided ID.
    - **422 Unprocessable Entity:** If the provided status payload is invalid.
    """
    return await repo_modify_laptop_status(id=id, laptop_status=laptop_status,
                                           db=db, admin=admin)


@router.delete("/delete-a-laptop", status_code=status.HTTP_200_OK)
async def api_delete_a_laptop(
        id: uuid.UUID, db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Delete a laptop record from the system. (Admin only)**

    This endpoint permanently removes a laptop record from the database based on
    its unique identifier. It should be used cautiously, as deletion cannot be reversed.
    Ideally, this action is restricted to administrators performing data cleanup or
    decommissioning tasks.

    **Args:**
    - **id (uuid.UUID):** The unique identifier of the laptop to be deleted.
    - **db (AsyncSession):** The asynchronous database session.
    - **admin (User):** The authenticated administrator performing the deletion.

    **Returns:**
    - **JSONResponse:** A success message confirming that the laptop was deleted.

    **Raises:**
    - **401 Unauthorized:** If the user is not authenticated or lacks admin privileges.
    - **404 Not Found:** If the laptop with the provided ID does not exist.

    """
    return await repo_delete_a_laptop(id, db, admin)
