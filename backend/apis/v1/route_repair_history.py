"""
# 🧰 Repair History Module

This module manages the **repair history** of laptops within the organization.
It provides endpoints to record, view, and retrieve repair-related information —
ensuring that all maintenance activities are properly logged and traceable.

## Functionality Overview

- **Create Repair Entry:**
  Records a new repair event for a specific laptop, including details such as
  issue description, repair date, cost, and technician information.

- **View All Repair Entries:**
  Retrieves a complete list of all recorded repairs, allowing administrators to
  monitor maintenance trends and costs across the organization.

- **View a Single Repair Entry:**
  Fetches detailed information for a specific repair record identified by its unique ID.

## Access Control
- Only **authenticated users** can interact with these endpoints.
- Creation and viewing of repair history may be restricted to **administrators** or
  **authorized maintenance staff**, depending on business rules.

## Response Models
All responses are validated against the `ShowRepairHistory` schema to ensure
consistency and data integrity across the API.
"""

import uuid

from fastapi import status, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository.repair_history import repo_create_entry, repo_show_an_entry, \
    repo_show_repairs
from db.sessions import get_db
from schemas.repair_history import CreateRepairHistory, ShowRepairHistory

router = APIRouter()


@router.put("/create-entry", response_model=ShowRepairHistory,
            status_code=status.HTTP_201_CREATED)
async def api_create_entry(
        entry: CreateRepairHistory, db: AsyncSession = Depends(get_db),
):
    """
    **Create a Repair History Entry**

    Creates a new repair record for a laptop.
    This endpoint allows authorized personnel to log details of a repair,
    including the issue encountered, repair actions taken, repair date, and the
    technician responsible.

    **Request Body:**
    - `laptop_id` (*UUID*): The unique identifier of the laptop being repaired.
    - `issue_description` (*str*): Description of the problem identified.
    - `repair_action` (*str*): The action or procedure taken to resolve the issue.
    - `repair_date` (*date*): The date the repair was completed.
    - `technician` (*str*): Name or identifier of the technician who performed the repair.
    - `remarks` (*Optional[str]*): Additional notes or comments about the repair.

    **Responses:**
    - **201 Created:** Returns the details of the newly created repair record.
    - **400 Bad Request:** If required fields are missing or invalid.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **422 Unprocessable Entity:** If the request body fails validation.

    **Returns:**
    A `ShowRepairHistory` object containing the created repair entry.

    **Authorization:**
    Requires authentication. Only administrators or authorized maintenance staff
    can create repair history entries.
    """

    return await repo_create_entry(entry, db)


@router.get("/show-entries", response_model=list[ShowRepairHistory],
            status_code=status.HTTP_202_ACCEPTED)
async def api_show_entries(db: AsyncSession = Depends(get_db)):
    """
    **Get All Repair History Entries**

    Retrieves a list of all recorded laptop repair history entries.
    This endpoint provides details of all repairs performed within the system,
    including the issue description, repair actions, date, and technician involved.

    **Query Parameters:**
    *None.*

    **Responses:**
    - **202 Accepted:** Returns a list of all repair history records.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **422 Unprocessable Entity:** If the request parameters are invalid.

    **Returns:**
    A list of `ShowRepairHistory` objects, each representing a recorded repair entry.

    **Authorization:**
    Requires authentication. Only administrators or authorized maintenance staff
    can access repair history data.
    """

    return await repo_show_repairs(db)


@router.get("show-entry", response_model=ShowRepairHistory,
            status_code=status.HTTP_202_ACCEPTED)
async def api_show_entry(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    **Get a Specific Repair History Entry**

    Retrieves detailed information about a single repair history entry using its unique identifier.
    This endpoint is used to view the repair record associated with a specific repair ID.

    **Query Parameters:**
    - `id` (*uuid*): The unique identifier of the repair history entry to retrieve.

    **Responses:**
    - **202 Accepted:** Returns the details of the specified repair history entry.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **404 Not Found:** If no repair entry exists for the provided ID.
    - **422 Unprocessable Entity:** If the provided ID format is invalid.

    **Returns:**
    A `ShowRepairHistory` object containing detailed repair information.

    **Authorization:**
    Requires authentication. Only administrators or authorized maintenance staff
    can view specific repair entries.
    """

    return await repo_show_an_entry(id, db)
