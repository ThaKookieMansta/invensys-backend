from fastapi import HTTPException, status, APIRouter,Depends, Query, UploadFile, File
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from fastapi.responses import StreamingResponse
import io

from db.sessions import get_db
from db.models.is_users import User
from db.repository.laptop_procurement import repo_new_laptop_purchase
from schemas.laptop_procurement import CreateLaptopProcurement, ShowLaptopProcurement, UploadPurchaseOrder
from apis.v1.route_login import get_current_user
from core.minio_client import minio_client, BUCKET_NAME

router = APIRouter()

@router.post("/add-procurement-record", response_model=ShowLaptopProcurement, status_code=status.HTTP_202_ACCEPTED)
async def api_add_procurement_record(record: CreateLaptopProcurement, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_user)):
    pass