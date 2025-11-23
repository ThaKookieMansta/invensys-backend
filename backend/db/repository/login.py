from time import strftime

from fastapi import HTTPException, status
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from db.models.is_users import User
from db.models.is_audit_logs import AuditLogs
from sqlalchemy import select

async def repo_get_user(username: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.username == username))
    app_user = result.scalar_one_or_none()
    if not app_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This is not authorized"
        )
    # new_audit_log = AuditLogs(
    #     user_id=app_user.id,
    #     action="Login",
    #     table_name="is_audit",
    #     record_id=app_user.id,
    #     details=f"{app_user.username}: logged into Invensys at {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    # )
    #
    # db.add(new_audit_log)
    # await db.commit()
    # await db.refresh(new_audit_log)


    return app_user

