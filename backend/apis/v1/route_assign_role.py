# from fastapi import HTTPException, status, APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from db.sessions import get_db
# from db.models.is_user_roles import UserRole
# from db.repository.user_role import repo_assign_role, repo_show_roles
# from schemas.user_role import CreateUserRole, ShowUserRole
# from apis.v1.route_login import get_current_user
#
# router = APIRouter()
#
# @router.post("/assign_role{user_id}/{role_id}", response_model=ShowUserRole, status_code=status.HTTP_200_OK)
# async def api_assign_role(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
#     return await repo_assign_role(user_id, role_id, db)
#
