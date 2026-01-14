import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apis.v1.route_login import get_current_user
from db.models.is_org_details import Department
from db.models.is_users import User
from db.repository.department import repo_get_department, \
    repo_delete_department, repo_update_department, repo_new_department, \
    repo_get_departments
from db.repository.user import repo_report_unauthorized_access
from db.sessions import get_db
from schemas.department import ShowDepartment, CreateDepartment

router = APIRouter()


@router.post("/add-department", response_model=ShowDepartment,
             status_code=status.HTTP_201_CREATED)
async def api_add_department(
        department: CreateDepartment,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
    **Add a Department**

    Creates a new department in the system.
    This endpoint is restricted to superusers and is typically used
    during organizational setup or administrative management.

    The department name is normalized before storage to ensure
    consistency across records.

    **Request Body:**
    - `department` (*CreateDepartment*): The department details to be created.

    **Responses:**
    - **201 Created:** The department was successfully created and returned.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester is not a superuser.

    **Returns:**
    The newly created department record.

    **Authorization:**
    Requires superuser privileges.

    """

    if not current_user.is_superuser:
        return repo_report_unauthorized_access(task_logged="Create Department",
                                               table_name="is_department",
                                               admin=current_user, db=db)

    return await repo_new_department(department, db, current_user)


@router.get("/get-a-department", response_model=ShowDepartment,
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_a_department(
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Get a Department**

    Retrieves the details of a specific department using its unique identifier.

    This endpoint allows authenticated users to view department information.
    Access control and visibility rules are enforced at the service layer.

    **Query Parameters:**
    - `id` (*UUID*): The unique identifier of the department to retrieve.

    **Responses:**
    - **202 Accepted:** Returns the requested department details.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **404 Not Found:** If no department exists with the provided ID.
    - **422 Unprocessable Entity:** If the provided ID format is invalid.

    **Returns:**
    The department record matching the provided identifier.

    **Authorization:**
    Requires authentication.
    """

    return await repo_get_department(
        id=id,
        db=db,
        admin=current_user
    )


@router.get("/get-all-departments", response_model=list[ShowDepartment],
            status_code=status.HTTP_202_ACCEPTED)
async def api_all_get_departments(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        department: Optional[str] = Query(None,
                                          description="Filter by Department Name"),
):

    """
    **Get All Departments**

    Retrieves a list of departments in the system with optional filtering.

    This endpoint allows authenticated users to view all available departments.
    Results can be filtered by department name to narrow down the response.

    **Query Parameters:**
    - `department` (*str, optional*): Filter results by department name.

    **Responses:**
    - **202 Accepted:** Returns a list of departments matching the filter criteria.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **422 Unprocessable Entity:** If the query parameter is invalid.

    **Returns:**
    A list of department records. If no departments match the filter,
    an empty list is returned.

    **Authorization:**
    Requires authentication.
    """
    return await repo_get_departments(
        db=db,
        admin=current_user,
        department=department
    )


@router.put("/update-department", response_model=ShowDepartment,
            status_code=status.HTTP_202_ACCEPTED)
async def api_update_department(
        new_department_name: CreateDepartment,
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
        **Update Department**

    Updates the name of an existing department.

    This endpoint allows an administrator to modify the name of a department
    identified by its unique ID. The new department name is provided in the
    request body and replaces the existing value.

    **Query Parameters:**
    - `id` (*UUID*): The unique identifier of the department to be updated.

    **Request Body:**
    - `department_name` (*str*): The new name to assign to the department.

    **Responses:**
    - **202 Accepted:** Returns the updated department details.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester does not have sufficient privileges.
    - **404 Not Found:** If no department exists with the provided ID.
    - **422 Unprocessable Entity:** If the request data is missing or invalid.

    **Returns:**
    The updated department record.

    **Authorization:**
    Requires administrator privileges.
    """
    return await repo_update_department(
        id=id,
        db=db,
        admin=current_user,
        new_department_name=new_department_name
    )


@router.delete("/delete-department", response_model=ShowDepartment,
               status_code=status.HTTP_202_ACCEPTED)
async def api_delete_department(
        id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
        **Delete Department**

    Removes a department from the system.

    This endpoint allows an administrator to delete an existing department
    identified by its unique ID. The deleted department is returned as part
    of the response for confirmation.

    **Query Parameters:**
    - `id` (*UUID*): The unique identifier of the department to be deleted.

    **Responses:**
    - **202 Accepted:** Returns the deleted department details.
    - **401 Unauthorized:** If the requester is not authenticated.
    - **403 Forbidden:** If the requester does not have sufficient privileges.
    - **404 Not Found:** If no department exists with the provided ID.
    - **422 Unprocessable Entity:** If the provided ID is invalid.

    **Returns:**
    The deleted department record.

    **Authorization:**
    Requires administrator privileges.
    """
    return await repo_delete_department(
        id=id,
        db=db,
        admin=current_user
    )
