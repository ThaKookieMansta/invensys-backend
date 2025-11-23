"""
### Laptop Procurement Module

This module manages the lifecycle of laptop procurement records within the system.
It enables administrators to record, upload, retrieve, and manage purchase-related information,
ensuring full traceability from acquisition to allocation.

**Core Functionalities:**
- Record new laptop procurement details (vendor, model, purchase date, PO number, etc.).
- Upload and link purchase order (PO) documents in PDF format to specific procurement records.
- Download existing PO files stored in the system.
- Retrieve individual or multiple procurement records with optional filters (e.g., vendor, PO, or date).

**Authorization:**
All endpoints in this module require **administrator privileges**.

**Endpoints Overview:**
- `POST /add-procurement-record` — Create a new procurement record.
- `PUT /upload-po` — Upload a purchase order document for an existing record.
- `GET /download-po` — Download the associated purchase order file.
- `GET /select-record` — Retrieve details of a single procurement record.
- `GET /search-records` — Search procurement records using optional filters.

This module supports centralized procurement tracking and document management,
integrating seamlessly with the laptop allocation and inventory systems.
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status, APIRouter, Depends, Query, \
    UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from apis.v1.route_login import get_current_user
from core.minio_client import minio_client, BUCKET_NAME
from db.models.is_users import User
from db.repository.laptop_procurement import repo_new_laptop_purchase, \
    repo_upload_purchase_order, repo_download_PO, repo_quiet_search, \
    repo_get_a_record, repo_get_records
from db.sessions import get_db
from schemas.laptop_procurement import CreateLaptopProcurement, \
    ShowLaptopProcurement

router = APIRouter()


@router.post("/add-procurement-record", response_model=ShowLaptopProcurement,
             status_code=status.HTTP_202_ACCEPTED)
async def api_add_procurement_record(
        record: CreateLaptopProcurement, db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Add a Laptop Procurement Record**

    Creates a new record for a laptop procurement entry in the system.
    This endpoint allows administrators to document details of newly purchased laptops,
    including procurement date, supplier, cost, and related metadata.

    **Request Body:**
    - `record` (*CreateLaptopProcurement*): JSON payload containing procurement details such as
      supplier name, purchase date, invoice number, total cost, and other relevant fields.

    **Responses:**
    - **202 Accepted:** Returns the details of the newly added procurement record.
    - **401 Unauthorized:** If the requester is not authenticated or lacks admin privileges.
    - **422 Unprocessable Entity:** If the provided data is incomplete or invalid.

    **Returns:**
    A `ShowLaptopProcurement` object representing the created procurement record.

    **Authorization:**
    Requires administrator privileges.
    """

    return await repo_new_laptop_purchase(
        procurement=record,
        db=db,
        admin=admin
    )


@router.put("/upload-po", status_code=status.HTTP_202_ACCEPTED)
async def api_upload_purchase_order(
        record_id: uuid.UUID,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Upload Purchase Order Document**

    Uploads a purchase order (PO) file and associates it with an existing laptop procurement record.
    This allows administrators to attach proof of purchase or vendor documentation for auditing purposes.
    If a file already exists for the record, the new upload will replace it.

    **Query Parameters:**
    - `record_id` (*uuid.UUID*): The unique identifier of the procurement record to which the PO file belongs.

    **Form Data:**
    - `file` (*UploadFile*): The purchase order document in PDF or other supported format.

    **Responses:**
    - **202 Accepted:** Returns a confirmation message and the stored object name of the uploaded file.
    - **401 Unauthorized:** If the requester is not authenticated or lacks admin privileges.
    - **404 Not Found:** If no procurement record exists for the provided ID.
    - **500 Internal Server Error:** If the file upload fails due to storage or network issues.

    **Returns:**
    A JSON object containing:
    ```json
    {
        "Message": "File Uploaded Successfully",
        "object_name": "<minio_path_to_uploaded_file>"
    }
    """

    if await repo_quiet_search(record_id, db, admin):
        object_name = f"purchase_orders/{record_id}/{uuid.uuid4()}_{file.filename}"

        try:
            minio_client.put_object(
                bucket_name=BUCKET_NAME,
                object_name=object_name,
                data=file.file,
                length=-1,
                part_size=10 * 1024 * 1024
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload Failed: {str(e)}"
            )
        record = await repo_upload_purchase_order(
            record_id=record_id,
            db=db,
            object_name=object_name,
            admin=admin
        )

        return {
            "Message": "File Uploaded Successfully",
            "object_name": record.purchase_order_file
        }


@router.get("/download-po", status_code=status.HTTP_202_ACCEPTED)
async def api_download_po(
        record_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Download Purchase Order Document**

    Downloads the purchase order (PO) file associated with a specific laptop procurement record.
    This allows administrators to retrieve and review the original uploaded purchase order document.
    The file is returned as a downloadable response if it exists in the system.

    **Query Parameters:**
    - `record_id` (*uuid.UUID*): The unique identifier of the procurement record whose PO document is being requested.

    **Responses:**
    - **202 Accepted:** Returns the requested purchase order file as a downloadable response.
    - **401 Unauthorized:** If the requester is not authenticated or lacks admin privileges.
    - **404 Not Found:** If the procurement record or associated file does not exist.
    - **422 Unprocessable Entity:** If the provided record ID format is invalid.

    **Returns:**
    A `FileResponse` containing the purchase order document.

    **Authorization:**
    Requires administrator privileges.
    """

    return await repo_download_PO(
        record_id=record_id,
        db=db,
        admin=admin
    )


@router.get("/select-record", response_model=ShowLaptopProcurement,
            status_code=status.HTTP_202_ACCEPTED)
async def api_select_record(
        record_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
):
    """
    **Retrieve a Specific Procurement Record**

    Fetches the details of a specific laptop procurement record by its unique identifier.
    This endpoint allows administrators to view complete procurement information, including
    purchase details and any associated purchase order document.

    **Query Parameters:**
    - `record_id` (*uuid.UUID*): The unique identifier of the procurement record to retrieve.

    **Responses:**
    - **202 Accepted:** Returns the procurement record details.
    - **401 Unauthorized:** If the requester is not authenticated or lacks admin privileges.
    - **404 Not Found:** If no procurement record exists for the provided ID.
    - **422 Unprocessable Entity:** If the provided record ID format is invalid.

    **Returns:**
    A `ShowLaptopProcurement` object containing the procurement record details.

    **Authorization:**
    Requires administrator privileges.
    """

    return await repo_get_a_record(record_id, db, admin)


@router.get(
    "/search-records",
    response_model=list[ShowLaptopProcurement],
    status_code=status.HTTP_202_ACCEPTED
)
async def api_search_records(
        db: AsyncSession = Depends(get_db),
        admin: User = Depends(get_current_user),
        purchase_order: Optional[str] = Query(None,
                                              description="Filter by purchase order"),
        purchase_date: Optional[datetime] = Query(None,
                                                  description="Filter bu date"),
        vendor: Optional[str] = Query(None, description="Filter by Vendor"),
):
    """
    **Search Procurement Records**

    Retrieves a list of laptop procurement records with optional filters.
    Administrators can search procurement history using purchase order number,
    purchase date, or vendor name. If no filters are applied, all procurement
    records are returned.

    **Query Parameters:**
    - `purchase_order` (*str*, optional): Filter results by the purchase order number.
    - `purchase_date` (*datetime*, optional): Filter results by the date of purchase.
    - `vendor` (*str*, optional): Filter results by the vendor’s name.

    **Responses:**
    - **202 Accepted:** Returns a list of procurement records matching the filters.
    - **401 Unauthorized:** If the requester is not authenticated or lacks admin privileges.
    - **422 Unprocessable Entity:** If any filter parameter is invalid.

    **Returns:**
    A list of `ShowLaptopProcurement` objects containing procurement details.

    **Authorization:**
    Requires administrator privileges.
    """

    return await repo_get_records(db, admin, purchase_order, purchase_date,
                                  vendor)
