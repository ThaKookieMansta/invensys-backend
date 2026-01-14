import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apis.v1.route_login import get_current_user
from db.models.is_users import User
from db.repository.business_unit import repo_get_business_unit, \
    repo_delete_business_unit, repo_update_business_unit, \
    repo_new_business_unit, repo_get_business_units
from db.repository.user import repo_report_unauthorized_access
from db.sessions import get_db
from schemas.business_unit import ShowBusinessUnit, CreateBusinessUnit

router = APIRouter()


@router.post("/add-business-unit", response_model=ShowBusinessUnit,
             status_code=status.HTTP_201_CREATED)
async def api_add_business_unit(
        business_unit: CreateBusinessUnit,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
        **Add Business Unit**

    Creates a new business unit in the system.

    This endpoint allows an administrator to define a new business unit
    that can later be associated with users, laptops, and other resources.

    **Request Body:**
    - `business_unit` (*CreateBusinessUnit*):
      The details of the business unit to be created.

    **Responses:**
    - **201 Created:** Returns the newly created business unit.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester does not have administrator privileges.
    - **422 Unprocessable Entity:** If the request body is missing or invalid.

    **Returns:**
    The created business unit record.

    **Authorization:**
    Requires administrator privileges.
    """
    if not current_user.is_superuser:
        return repo_report_unauthorized_access(
            task_logged="Add Business Unit",
            table_name="is_business_unit",
            admin=current_user,
            db=db
        )
    return await repo_new_business_unit(
        business_unit=business_unit,
        db=db,
        admin=current_user
    )


@router.get("/get-all-business-units", response_model=list[ShowBusinessUnit],
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_all_business_units(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        business_unit: Optional[str] = Query(None,
                                             description="Filter by Business Unit"),
):

    """
        **Get Business Units**

    Retrieves a list of business units in the system, optionally filtered by name.

    This endpoint allows administrators to fetch all business units, or filter
    by a specific name using the query parameter. Returns an empty list if
    no matching records are found.

    **Query Parameters:**
    - `business_unit` (*str, optional*): Filter business units by name.

    **Responses:**
    - **202 Accepted:** Returns a list of business units matching the filter.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester does not have administrator privileges.
    - **422 Unprocessable Entity:** If the query parameter is invalid.

    **Returns:**
    A list of business unit records.

    **Authorization:**
    Requires administrator privileges.
    """
    return await repo_get_business_units(
        db=db,
        admin=current_user,
        business_unit=business_unit
    )


@router.get("/get-a-business-unit", response_model=ShowBusinessUnit,
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_a_business_unit(
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
        **Get a Business Unit**

    Retrieves the details of a specific business unit by its unique identifier.

    This endpoint allows administrators to fetch a single business unit record
    using its UUID. Returns a 404 error if no matching business unit exists.

    **Query Parameters:**
    - `id` (*UUID*): The unique identifier of the business unit to retrieve.

    **Responses:**
    - **202 Accepted:** Returns the business unit details.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester does not have administrator privileges.
    - **404 Not Found:** If no business unit exists with the provided ID.
    - **422 Unprocessable Entity:** If the provided ID is invalid.

    **Returns:**
    The business unit record.

    **Authorization:**
    Requires administrator privileges.
    """
    return await repo_get_business_unit(
        id=id,
        db=db,
        admin=current_user
    )


@router.put("/update-business-unit-name", response_model=ShowBusinessUnit,
            status_code=status.HTTP_202_ACCEPTED)
async def api_update_business_unit_name(
        new_unit_name: CreateBusinessUnit,
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),

):

    """
        **Update Business Unit Name**

    Updates the name of an existing business unit.

    This endpoint allows administrators to change the name of a business unit
    identified by its UUID. The new name is provided in the request body.
    Returns a 404 error if the business unit does not exist.

    **Query Parameters:**
    - `id` (*UUID*): The unique identifier of the business unit to update.

    **Request Body:**
    - `new_unit_name` (*CreateBusinessUnit*): The new name for the business unit.

    **Responses:**
    - **202 Accepted:** Returns the updated business unit record.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester does not have administrator privileges.
    - **404 Not Found:** If no business unit exists with the provided ID.
    - **422 Unprocessable Entity:** If the request body or ID is invalid.

    **Returns:**
    The updated business unit record.

    **Authorization:**
    Requires administrator privileges.
    """

    return await repo_update_business_unit(
        id=id,
        db=db,
        admin=current_user,
        new_unit_name=new_unit_name
    )


@router.delete("/delete-business-unit", response_model=ShowBusinessUnit,
               status_code=status.HTTP_202_ACCEPTED)
async def api_delete_business_unit(
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
        **Delete a Business Unit**

    Permanently removes a business unit from the system.

    This endpoint allows administrators to delete a business unit identified by its UUID.
    Use with caution, as this action is irreversible. Any dependencies or references
    to the business unit should be handled appropriately.

    **Query Parameters:**
    - `id` (*UUID*): The unique identifier of the business unit to be deleted.

    **Responses:**
    - **202 Accepted:** Returns confirmation and details of the deleted business unit.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester does not have administrator privileges.
    - **404 Not Found:** If no business unit exists with the provided ID.
    - **422 Unprocessable Entity:** If the provided ID is invalid.

    **Returns:**
    The deleted business unit record.

    **Authorization:**
    Requires administrator privileges.
    """
    return await repo_delete_business_unit(
        id=id,
        db=db,
        admin=current_user
    )
