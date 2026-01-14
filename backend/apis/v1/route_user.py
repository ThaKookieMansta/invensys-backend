"""
User API Endpoints.

This module defines the API routes for managing users within the system.
It provides endpoints for creating, retrieving, updating, and deleting users,
as well as handling authentication-related actions such as password changes.

Endpoints:
    POST /create-user
        Create a new user in the system. Requires administrator rights.

    GET /get-a-user
        Retrieve details of a specific user by username.

    GET /get-all-users
        Retrieve a list of users with optional filters such as username,
        business unit, department, and active status.

    PUT /change-user-password
        Allows an administrator to change another user's password.

    PUT /change-my-password
        Allows an authenticated user to change their own password.

    PUT /change-user-status
        Update a user's status (active/inactive). Requires administrator rights.

    PUT /change-user-permission
        Change a user's permission level (normal ↔ superuser).
        Requires administrator rights.

    DELETE /delete-a-user
        Permanently delete a user from the system. Requires administrator rights.

Usage:
    from apis.v1 import route_user
    api_router.include_router(route_user.router, prefix="", tags=["User"])
"""

from typing import Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apis.v1.route_login import get_current_user
from db.models.is_users import User
from db.repository.user import repo_create_user, repo_get_a_user, \
    repo_delete_a_user, repo_get_all_users, repo_change_user_password, \
    repo_change_user_status, repo_change_user_permission, \
    repo_report_unauthorized_access, repo_change_my_password, repo_update_user
from db.sessions import get_db
from schemas.user import CreateUser, ShowUser, ChangePassword, ModifyUser

router = APIRouter()


@router.post("/create-user", response_model=ShowUser,
             status_code=status.HTTP_201_CREATED)
async def api_create_user(
        user: CreateUser, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Create User**

    Creates a new user in the system.
    Only administrators are authorized to perform this action.

    **Request Body:**
    - `first_name` (*str*, required): The user's first name.
    - `last_name` (*str*, required): The user's last name.
    - `username` (*str*, required): The unique username for the user.
    - `email_address` (*str*, required): The user's email address.
    - `password_hash` (*str*, optional): The hashed password. If `null`, the user will not have login rights.
    - `business_unit` (*str*, required): The business unit the user belongs to.
    - `department` (*str*, required): The department the user belongs to.

    **Responses:**
    - **201 Created:** Returns the details of the newly created user.
    - **401 Unauthorized:** If the requester is not authenticated or not an admin.
    - **422 Unprocessable Entity:** If any field is missing or invalid.

    **Returns:**
    `ShowUser` — The details of the newly created user.

    **Authorization:**
    Requires administrator privileges.
    """
    if not current_user.is_superuser:
        return repo_report_unauthorized_access(task_logged="User Creation",
                                               table_name="is_user",
                                               admin=current_user, db=db)
    return await repo_create_user(user, db, current_user)


@router.get("/get-a-user", response_model=ShowUser,
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_a_user(
        username: str, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Get a User**

    Retrieves the details of a specific user by their username.
    Only administrators are authorized to perform this action.

    **Query Parameters:**
    - `username` (*str*, required): The unique username of the user to retrieve.

    **Responses:**
    - **200 OK:** Returns the details of the requested user.
    - **401 Unauthorized:** If the requester is not authenticated or not an admin.
    - **422 Unprocessable Entity:** If the `username` parameter is missing or invalid.

    **Returns:**
    `ShowUser` — The details of the specified user.

    **Authorization:**
    Requires administrator privileges.
    """

    return await repo_get_a_user(username, db, current_user)


@router.get("/get-all-users", response_model=list[ShowUser],
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_all_users(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        is_active: Optional[bool] = Query(None,
                                          description="Filter by User status"),
        username: Optional[str] = Query(None,
                                        description="Filter by Username"),
):
    """
    **Get All Users**

    Retrieves a list of users in the system, with optional filters.
    Only administrators are authorized to perform this action.

    **Query Parameters:**
    - `username` (*str*, optional): Filter by a specific username.
    - `is_active` (*bool*, optional): Filter users by active status (`true` or `false`).

    **Responses:**
    - **200 OK:** Returns a list of users matching the provided filters, or all users if no filters are applied.
    - **401 Unauthorized:** If the requester is not authenticated or not an admin.
    - **422 Unprocessable Entity:** If any filter parameter is invalid.

    **Returns:**
    `list[ShowUser]` — A list of user records matching the filters.

    **Authorization:**
    Requires administrator privileges.
    """

    return await repo_get_all_users(
        db=db,
        admin=current_user,
        is_active=is_active,
        username=username,
    )


@router.put("/change-user-password", response_model=ShowUser,
            status_code=status.HTTP_202_ACCEPTED)
async def api_change_user_password(
        username: str, password: ChangePassword,
        db: AsyncSession = Depends(get_db), current_user: User = Depends(
            get_current_user),
):
    """
    **Change User Password**

    Changes the password of a specific user.
    Only administrators are authorized to perform this action.

    **Request Body:**
    - `username` (*str*): The username of the user whose password will be changed.
    - `password` (*str*): The new password for the user.

    **Responses:**
    - **200 OK:** Returns a confirmation message indicating successful password change.
    - **401 Unauthorized:** If the requester is not authenticated or not an admin.
    - **422 Unprocessable Entity:** If the request body is missing or invalid.

    **Returns:**
    `dict` — Confirmation message of successful password update.

    **Authorization:**
    Requires administrator privileges.
    """

    if not current_user.is_superuser:
        return await repo_report_unauthorized_access(
            task_logged="Password Change", table_name="is_user",
            admin=current_user, db=db)
    return await repo_change_user_password(username, password, db,
                                           admin=current_user)


@router.put("/change-my-password", response_model=ShowUser,
            status_code=status.HTTP_202_ACCEPTED)
async def api_change_my_password(
        new_password: ChangePassword,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
    **Change My Password**

    Allows an authenticated user to change their own password.
    The current password must be provided for verification, and the new password will be securely hashed in the service layer.

    **Request Body:**
    - `current_password` (*str*): The user's current plain-text password (used for verification).
    - `new_password` (*str*): The new plain-text password to be securely stored.

    **Responses:**
    - **200 OK:** Returns a confirmation message indicating successful password change.
    - **401 Unauthorized:** If the requester is not logged in, or the current password is incorrect.
    - **422 Unprocessable Entity:** If the request body is missing or invalid.

    **Returns:**
    `dict` — Confirmation message of successful password update.

    **Authorization:**
    Requires authentication (logged-in user).
    """

    return await repo_change_my_password(new_password, db, user=current_user)


@router.put("/change-user-status", response_model=ShowUser,
            status_code=status.HTTP_202_ACCEPTED)
async def api_change_user_status(
        username: str, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Change User Status**

    Allows an administrator to activate or deactivate a user account.
    This is typically used when a user leaves or rejoins the organization.

    **Query Parameters:**
    - `username` (*str*): The username of the user whose status is to be updated.

    **Responses:**
    - **200 OK:** Returns confirmation of the status change along with updated user details.
    - **401 Unauthorized:** If the requester is not authenticated or does not have admin privileges.
    - **422 Unprocessable Entity:** If the provided username is missing or invalid.

    **Returns:**
    `ShowUser` — Updated user details reflecting the new status.

    **Authorization:**
    Requires administrator privileges.
    """

    if not current_user.is_superuser:
        return await repo_report_unauthorized_access(
            task_logged="Activate / Deactivate User", table_name="is_user",
            admin=current_user, db=db)
    return await repo_change_user_status(username, db, admin=current_user)


@router.put("/change-user-permission", response_model=ShowUser,
            status_code=status.HTTP_202_ACCEPTED)
async def api_change_user_permission(
        username: str, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
    **Change User Permission**

    Allows an administrator to modify a user’s permission level.
    This endpoint toggles a user between a normal user role and a superuser role.

    **Query Parameters:**
    - `username` (*str*): The username of the user whose permission level is to be updated.

    **Responses:**
    - **200 OK:** Returns confirmation of the permission change along with the updated user details.
    - **401 Unauthorized:** If the requester is not authenticated or does not have admin privileges.
    - **422 Unprocessable Entity:** If the provided username is missing or invalid.

    **Returns:**
    `ShowUser` — Updated user details reflecting the new permission level.

    **Authorization:**
    Requires administrator privileges.
    """

    if not current_user.is_superuser:
        return await repo_report_unauthorized_access(
            task_logged="Elevate / Demote User", table_name="is_user",
            admin=current_user, db=db)
    return await repo_change_user_permission(username, db, admin=current_user)


@router.put("/update-a-user", response_model=ShowUser,
            status_code=status.HTTP_202_ACCEPTED)
async def api_update_a_user(
        updated_data: ModifyUser,
        username: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    if not current_user.is_superuser:
        return repo_report_unauthorized_access(
            task_logged="Modify user details",
            table_name="is_user",
            admin=current_user,
            db=db
        )

    return await repo_update_user(updated_user=updated_data, username=username,
                                  db=db, admin=current_user)


@router.delete("/delete-a-user", status_code=status.HTTP_202_ACCEPTED)
async def api_delete_a_user(
        username: str, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    """
    **Delete a User**

    Allows an administrator to permanently remove a user from the system.
    This operation is irreversible and should be used with caution.
    Frontend confirmation (if any) is handled outside this endpoint.

    **Query Parameters:**
    - `username` (*str*): The username of the user to be deleted.

    **Responses:**
    - **200 OK:** Returns confirmation that the user has been successfully deleted.
    - **401 Unauthorized:** If the requester is not authenticated or does not have admin privileges.
    - **422 Unprocessable Entity:** If the provided username is missing or invalid.

    **Returns:**
    A success message confirming the user’s deletion.

    **Authorization:**
    Requires administrator privileges.
    """

    if not current_user.is_superuser:
        return await repo_report_unauthorized_access(task_logged="Delete User",
                                                     table_name="is_user",
                                                     admin=current_user, db=db)

    return await repo_delete_a_user(username, db, admin=current_user)
