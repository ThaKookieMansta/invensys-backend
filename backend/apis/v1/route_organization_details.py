"""
Organization Management Routes.

This module defines API endpoints for managing organization records in the system.
It allows administrators to create, retrieve, list, and update organization details
such as the organization name and address information.

Organizations represent top-level entities within the system and are used to
structure business units, departments, users, and asset ownership.

Responsibilities of this module:
- Expose organization-related API endpoints
- Enforce authentication and administrator authorization
- Validate request payloads using Pydantic schemas
- Delegate all business logic and database operations to the repository layer
- Return consistent API responses for client consumption

Authorization:
    All endpoints in this module require authentication.
    Only administrators (superusers) are permitted to create, update, or retrieve
    organization records.

Notes:
    - This module focuses solely on request handling and access control.
    - Business rules, validation, and persistence are implemented in the
      repository/service layer.
    - Swagger/OpenAPI documentation is generated from the route definitions and
      docstrings provided here.

Endpoints:
    - POST   /add-organization
    - GET    /get-organization-details
    - GET    /list-organizations
    - PUT    /update-organization-details
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apis.v1.route_login import get_current_user
from db.models.is_users import User
from db.repository.organization import repo_update_organization, \
    repo_add_organization, repo_get_organization_details, \
    repo_list_organizations
from db.repository.user import repo_report_unauthorized_access
from db.sessions import get_db
from schemas.orgdetails import AddOrganization, ModifyOrganization, \
    ShowOrganization

router = APIRouter()


@router.post("/add-organization", response_model=ShowOrganization,
             status_code=status.HTTP_201_CREATED)
async def api_add_organization(
        organization: AddOrganization, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Create an Organization**

    Creates a new organization record in the system.

    This endpoint allows administrators to define an organization that serves as
    the top-level entity for structuring business units, departments, users,
    and assets within the system.

    **Request Body:**
    - `organization` (*AddOrganization*): Schema containing the organization details
      such as name and any additional metadata.

    **Responses:**
    - **201 Created:** Returns the newly created organization details.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester does not have administrator privileges.
    - **422 Unprocessable Entity:** If the request body is missing or invalid.

    **Returns:**
    The newly created organization record.

    **Authorization:**
    Requires administrator privileges.

    """
    if not current_user.is_superuser:
        return await repo_report_unauthorized_access(
            task_logged="Company Creation",
            table_name="is_organizationdetails",
            admin=current_user, db=db)
    return await repo_add_organization(organization=organization, db=db,
                                       admin=current_user)


@router.get("/get-organization-details", response_model=ShowOrganization,
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_organization_details(
        id: uuid.UUID, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        **Get Organization Details**

    Retrieves the details of a specific organization using its unique identifier.

    This endpoint allows administrators to view organization information,
    including core metadata required to structure business units, departments,
    users, and assets within the system.

    **Query Parameters:**
    - `id` (*UUID*): The unique identifier of the organization to retrieve.

    **Responses:**
    - **202 Accepted:** Returns the organization details.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **404 Not Found:** If no organization exists for the provided ID.
    - **422 Unprocessable Entity:** If the provided ID format is invalid.

    **Returns:**
    The organization record matching the provided ID.

    **Authorization:**
    Requires authentication. Administrator privileges may be enforced depending
    on access control rules.
    """
    return repo_get_organization_details(id, db, current_user)


@router.get("/list-organizations", response_model=list[ShowOrganization],
            status_code=status.HTTP_202_ACCEPTED)
async def api_list_organizations(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        **List Organizations**

    Retrieves all organizations registered in the system.

    This endpoint allows authenticated users to view the list of organizations.
    It is typically used during system setup or administrative management to
    understand the organizational structure configured within the platform.

    **Responses:**
    - **202 Accepted:** Returns a list of all organizations.
    - **401 Unauthorized:** If the requester is not authenticated.

    **Returns:**
    A list of organization records available in the system.

    **Authorization:**
    Requires authentication.
    """
    return await repo_list_organizations(db, current_user)


@router.put("/update-organization-details", response_model=ShowOrganization,
            status_code=status.HTTP_202_ACCEPTED)
async def api_update_organization(
        organization_updates: ModifyOrganization,
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        **Update Organization Details**

        Updates the details of an existing organization in the system.

        This endpoint allows administrators to modify organization information.
        Only fields provided in the request body will be updated; all other fields
        will remain unchanged.

        **Path / Query Parameters:**
        - `id` (*UUID*): The unique identifier of the organization to be updated.

        **Request Body:**
        - `ModifyOrganization`: JSON payload containing one or more of the following fields:
            - `organization_name` (*str*, optional): Updated organization name.
            - `street_address` (*str*, optional): Updated street or physical address.
            - `po_box` (*str*, optional): Updated postal address (P.O. Box).

        **Responses:**
        - **202 Accepted:** Returns the updated organization details.
        - **401 Unauthorized:** If the requester is not authenticated or lacks admin privileges.
        - **404 Not Found:** If no organization exists for the provided ID.
        - **422 Unprocessable Entity:** If the request body or ID is invalid.

        **Returns:**
        The updated organization record.

        **Authorization:**
        Requires administrator privileges.
    """
    if not current_user.is_superuser:
        return repo_report_unauthorized_access(
            task_logged="Modify Organization details",
            table_name="is_organizationdetails",
            admin=current_user,
            db=db
        )
    return await repo_update_organization(id=id,
                                          updated_organization=organization_updates,
                                          db=db, admin=current_user)
