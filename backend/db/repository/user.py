import random
import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models.is_audit_logs import AuditLogs
from db.models.is_org_details import Department, BusinessUnit
from db.models.is_users import User
from schemas.user import CreateUser, ChangePassword, ModifyUser
from core.hashing import Hasher
from core.logging_config import logger
from datetime import datetime


async def repo_create_user(user: CreateUser, db: AsyncSession, admin: User):
    existing_username = await db.execute(
        select(User).where(User.username == user.username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The username: {user.username} already exists"
        )

    existing_email = await db.execute(
        select(User).where(User.email_address == user.email_address))
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The email address: {user.email_address} already exists"
        )

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username.lower(),
        email_address=user.email_address,
        password_hash=Hasher.hash_password(user.password_hash),
        business_unit_id=user.business_unit_id,
        department_id=user.department_id,
    )

    db.add(new_user)

    logger.info(f"{new_user.username} has been created by {admin.username}")

    await db.commit()
    await db.refresh(new_user)
    return new_user


async def repo_get_a_user(username: str, db: AsyncSession, admin: User):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"!!! {username} DOES NOT EXIST!!!"
        )
    logger.info(f"{admin.username}: Opened details for user {username}")

    return user


async def repo_get_all_users(
        db: AsyncSession,
        admin: User,
        is_active: Optional[bool] = None,
        username: Optional[str] = None,

):

    details = f"{admin.username} searched through all users"

    query = select(User)

    if is_active is not None:
        query = query.where(User.is_active == is_active)
        details = f"{details}: User status = {is_active}"
    if username:
        query = query.where(User.username == username)
        details = f"{details}: Username = {username}"

    result = await db.execute(query)

    logger.info(details)

    return result.scalars().all()


async def repo_change_user_password(
        username: str, password: ChangePassword, db: AsyncSession, admin: User,
):
    my_user = select(User).where(User.username == username)
    result = await db.execute(my_user)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"!!! {username} DOES NOT EXIST!!!"
        )

    user.password_hash = Hasher.hash_password(password.new_password)
    user.modified_at = datetime.now()

    logger.info(f"{admin.username} modified the password for {username}")

    await db.commit()
    await db.refresh(user)
    return user


async def repo_update_user(
        updated_user: ModifyUser,
        username: str,
        db: AsyncSession,
        admin: User,
):
    result = await db.execute(select(User).where(User.username == username))
    user_result = result.scalar_one_or_none()

    if not user_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"!!! {username} DOES NOT EXIST!!!"
        )
    update_data = updated_user.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_result, field, value)

    user_result.modified_at = datetime.now()

    logger.info(f"{admin.username}: Updated user info for {username}")

    await db.commit()
    await db.refresh(user_result)
    return user_result


async def repo_change_my_password(
        password: ChangePassword, db: AsyncSession, user: User,
):
    if not Hasher.verify_password(plain_password=password.current_password,
                                  hashed_password=user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your current password is incorrect"
        )

    user.password_hash = Hasher.hash_password(password.new_password)
    user.modified_at = datetime.now()

    logger.info(f"{user.username}: Modified their own password")

    await db.commit()
    await db.refresh(user)
    return user


async def repo_delete_a_user(username: str, db: AsyncSession, admin: User):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"!!! {username} DOES NOT EXIST!!!"
        )

    logger.info(f"{admin.username} deleted the user {username}")

    await db.delete(user)
    await db.commit()
    return {"msg": f"Deleted user '{username}'"}


async def repo_change_user_status(
        username: str, db: AsyncSession, admin: User,
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"!!! {username} DOES NOT EXIST!!!"
        )
    user.is_active = not user.is_active
    user.modified_at = datetime.now()

    logger.info(
        f"{admin.username} Activated / Deactivated the user {username}")

    await db.commit()
    await db.refresh(user)
    return user


async def repo_change_user_permission(
        username: str, db: AsyncSession, admin: User,
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"!!! {username} DOES NOT EXIST!!!"
        )

    user.is_superuser = not user.is_superuser
    user.modified_at = datetime.now()

    logger.info(f"{admin.username} Promoted / Demoted the user {username}")

    await db.commit()
    await db.refresh(user)
    return user


async def repo_report_unauthorized_access(
        task_logged: str, table_name: str, admin: User, db: AsyncSession,
):
    logger.info(f"{admin.username} attempted a {task_logged} but was blocked")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You are not authorized to perform this task. Your action has been logged"
    )
