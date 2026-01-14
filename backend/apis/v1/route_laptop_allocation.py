"""
Module: route_laptop_allocation
===============================

This module defines all API endpoints related to laptop allocations within the organization.
It enables administrators to create and manage allocation records, handle return processes,
and generate or upload associated signed forms for verification and documentation.

Usage:
    from apis.v1 import route_laptop_allocation
    api_router.include_router(route_laptop_allocation.router, prefix="", tags=["Laptop Allocation"])

Endpoints
----------

POST Endpoints
---------------

1. /create-allocation
   ------------------
   Creates a new laptop allocation record for a specific user and device.
   Only administrators can perform this operation.

   Args:
       allocation (CreateAllocation): Allocation details including user and laptop information.
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       ShowAllocations: The newly created allocation record.

   Raises:
       HTTPException:
           - 401 Unauthorized: If user is not authenticated.
           - 422 Unprocessable Entity: If validation fails.

PUT Endpoints
--------------

1. /return-laptop
   ---------------
   Updates an existing allocation to mark a laptop as returned.
   Captures return details including comments or reason fields.

   Args:
       id (uuid.UUID): The allocation ID.
       returned_laptop (CreateReturn): Return details such as condition and comments.
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       ShowAllocations: The updated allocation record.

   Raises:
       HTTPException:
           - 401 Unauthorized: If user is not authenticated.
           - 404 Not Found: If the allocation record is missing.

2. /upload-allocation-form
   ------------------------
   Uploads a signed allocation form file for a specific allocation.
   Any new upload replaces the existing document.

   Args:
       alloc_id (uuid.UUID): The allocation ID.
       file (UploadFile): The signed allocation form (PDF).
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       JSONResponse: Success message confirming upload.

   Raises:
       HTTPException:
           - 400 Bad Request: If file type or allocation is invalid.
           - 401 Unauthorized: If user is not authenticated.

3. /upload-return-form
   --------------------
   Uploads a signed return form file for a specific allocation return record.
   New uploads overwrite any previous version.

   Args:
       alloc_id (uuid.UUID): The allocation ID.
       file (UploadFile): The signed return form (PDF).
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       JSONResponse: Success message confirming upload.

   Raises:
       HTTPException:
           - 400 Bad Request: If file type or allocation is invalid.
           - 401 Unauthorized: If user is not authenticated.

GET Endpoints
--------------

1. /get-allocation
   ----------------
   Retrieves a specific laptop allocation record by its unique identifier.

   Args:
       id (uuid.UUID): Allocation ID.
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       ShowAllocations: The requested allocation record.

   Raises:
       HTTPException:
           - 401 Unauthorized: If user is not authenticated.
           - 404 Not Found: If allocation does not exist.

2. /get-allocations
   -----------------
   Retrieves all allocation records, with optional filters for status or identifiers.

   Args:
       is_active (Optional[bool]): Filter allocations by active/inactive status.
       username (Optional[str]): Filter by username.
       serial_number (Optional[str]): Filter by laptop serial number.
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       list[ShowAllocations]: A list of allocation records.

   Raises:
       HTTPException:
           - 401 Unauthorized: If user is not authenticated.

3. /download-allocation-form
   --------------------------
   Downloads the signed allocation form for a given allocation record.

   Args:
       id (uuid.UUID): Allocation ID.
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       FileResponse: The PDF allocation form.

   Raises:
       HTTPException:
           - 401 Unauthorized: If user is not authenticated.
           - 404 Not Found: If file not found.

4. /download-return-form
   ----------------------
   Downloads the signed return form associated with a given allocation.

   Args:
       id (uuid.UUID): Allocation ID.
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       FileResponse: The PDF return form.

   Raises:
       HTTPException:
           - 401 Unauthorized: If user is not authenticated.
           - 404 Not Found: If file not found.

5. /generate-form
   ----------------
   Generates either an allocation or return form dynamically as a PDF document
   using allocation details stored in the database.

   Args:
       allocation_id (uuid.UUID): The allocation ID.
       form_type (str): Either "allocation" or "return".
       db (AsyncSession): Database session.
       current_user (User): Authenticated user.

   Returns:
       FileResponse: The generated PDF document.

   Raises:
       HTTPException:
           - 400 Bad Request: Invalid form type.
           - 401 Unauthorized: If user is not authenticated.
           - 404 Not Found: If allocation record does not exist.

DELETE Endpoints
-----------------
(None currently implemented)
"""

import io
import uuid
from typing import Optional

from fastapi import HTTPException, status, APIRouter, Depends, Query, \
    UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from apis.v1.route_login import get_current_user
from core.minio_client import minio_client, BUCKET_NAME
from db.models.is_users import User
from db.repository.laptop_allocation import repo_create_allocation, \
    repo_show_all_allocations, repo_return_laptop, repo_show_an_allocation, \
    repo_upload_form, repo_download_form, repo_upload_return_form, \
    repo_download_return_form, repo_create_allocation_form, \
    repo_create_return_form
from db.repository.organization import repo_get_organization_name
from db.sessions import get_db
from schemas.laptop_allocation import CreateAllocation, ShowAllocations, \
    CreateReturn
from core.branding import get_logo_path

router = APIRouter()


@router.post("/create-allocation", response_model=ShowAllocations,
             status_code=status.HTTP_201_CREATED)
async def api_create_allocation(
        allocation: CreateAllocation, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Create a New Laptop Allocation**

    Creates a new laptop allocation record in the system.

    This endpoint assigns a laptop to a specific user based on the provided allocation details.
    Only administrators are authorized to perform this action.

    **Request Body:**
    - `user_id` (UUID): The ID of the user receiving the laptop.
    - `laptop_id` (UUID): The ID of the laptop being allocated.
    - `start_date` (date): The start date of the allocation.
    - `expected_return_date` (date): The expected date of laptop return.

    **Responses:**
    - **201 Created:** Returns the details of the newly created allocation.
    - **401 Unauthorized:** The requester is not authenticated or not an admin.
    - **422 Unprocessable Entity:** The allocation data is invalid or the laptop is already assigned.
    """

    return await repo_create_allocation(allocation, db, current_user.id)


@router.put("/return-laptop", response_model=ShowAllocations,
            status_code=status.HTTP_202_ACCEPTED)
async def api_return_laptop(
        id: uuid.UUID,
        returned_laptop: CreateReturn,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Return a Laptop**

    Marks a laptop as returned and updates the allocation record accordingly.

    This endpoint allows an administrator to process the return of an allocated laptop.
    It records the return details, including the return date and any comments or reasons (e.g., if the laptop was damaged).
    Once processed, the allocation is marked as inactive and the laptop becomes available for reassignment.

    **Note:**
    The signed return document is not uploaded through this endpoint.
    It should be uploaded separately using the designated document upload endpoint.

    **Request Parameters:**
    - `id` (UUID): The unique identifier of the laptop allocation being returned.

    **Request Body:**
    - `return_date` (date): The date when the laptop was returned.
    - `comments` (str, optional): Additional details or reasons for the return (e.g., damage).

    **Responses:**
    - **202 Accepted:** Returns the updated allocation record reflecting the laptop’s return status.
    - **401 Unauthorized:** The requester is not authenticated or not an admin.
    - **404 Not Found:** No allocation exists for the provided ID.
    - **422 Unprocessable Entity:** Invalid return data.

    **Authorization:**
    Administrator privileges required.
    """

    return await repo_return_laptop(
        id=id,
        returned_laptop=returned_laptop,
        db=db,
        allocator_id=current_user.id
    )


@router.put("/upload-allocation-form", status_code=status.HTTP_202_ACCEPTED)
async def api_upload_allocation_form(
        alloc_id: uuid.UUID, file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db), current_user: User = Depends(
            get_current_user),
):
    """
    **Upload Allocation Form**

    Uploads a signed laptop allocation form and attaches it to an existing allocation record.

    This endpoint is used during the laptop allocation process.
    It allows administrators to upload the signed PDF allocation form corresponding to a specific allocation.
    If a new file is uploaded for the same allocation, it replaces the previously uploaded document.

    **Note:**
    The allocation form is generated separately using the `/generate-form` endpoint,
    which creates the unsigned document based on allocation details before signing and upload.

    **Request Parameters:**
    - `alloc_id` (UUID): The unique identifier of the allocation associated with the uploaded file.

    **Request Body:**
    - `file` (UploadFile): The signed allocation form in PDF format.

    **Responses:**
    - **202 Accepted:** Confirmation message indicating successful upload and linkage of the file.
    - **400 Bad Request:** The uploaded file is missing or not in PDF format.
    - **401 Unauthorized:** The requester is not authenticated or not an admin.
    - **404 Not Found:** No allocation exists for the provided ID.
    - **422 Unprocessable Entity:** Error saving or linking the uploaded file.

    **Authorization:**
    Administrator privileges required.
    """

    object_name = f"allocation_forms/{alloc_id}/{uuid.uuid4()}_{file.filename}"

    try:
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

    allocation = await repo_upload_form(
        id=alloc_id,
        db=db,
        object_name=object_name,
        admin=current_user
    )

    return {
        "message": "File Uploaded Successfully",
        "object_name": allocation.allocation_form,
    }


@router.put("/upload-return-form", status_code=status.HTTP_202_ACCEPTED)
async def api_upload_return_form(
        alloc_id: uuid.UUID, file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Upload Return Form**

    Uploads the signed laptop return form for a completed allocation.

    This endpoint allows administrators to upload a signed PDF document confirming
    the return of a previously allocated laptop. The uploaded file replaces any existing
    return form linked to the allocation record.

    **Request Parameters:**
    - `alloc_id` (UUID): The unique identifier of the allocation whose return form is being uploaded.

    **Request Body:**
    - `file` (UploadFile): The signed return form in PDF format.

    **Responses:**
    - **202 Accepted:** Confirmation message indicating successful upload and association with the allocation.
    - **401 Unauthorized:** The requester is not authenticated or not an admin.
    - **404 Not Found:** The allocation record does not exist.
    - **422 Unprocessable Entity:** The uploaded file is invalid or missing.

    **Authorization:**
    Administrator privileges required.
    """

    object_name = f"return_forms/{alloc_id}/{uuid.uuid4()}_{file.filename}"

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

    allocation = await repo_upload_return_form(
        id=alloc_id,
        db=db,
        object_name=object_name,
        admin=current_user
    )

    return {
        "Message": "File uploaded successfully",
        "object_name": allocation.return_form,
    }


@router.get("/get-allocation", response_model=ShowAllocations,
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_allocation(
        id: uuid.UUID, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Get Allocation Details**

    Retrieves the details of a specific laptop allocation using its unique identifier.

    This endpoint allows administrators to fetch an allocation record by its ID.
    It returns detailed allocation information, including the assigned user,
    associated laptop, allocation dates, and current status.

    **Request Parameters:**
    - `id` (UUID): The unique identifier of the allocation to retrieve.

    **Responses:**
    - **200 OK:** Returns the details of the requested laptop allocation, including related user and laptop information.
    - **401 Unauthorized:** The requester is not authenticated or not an admin.
    - **404 Not Found:** No allocation exists for the provided ID.
    - **422 Unprocessable Entity:** The provided ID format is invalid.

    **Authorization:**
    Administrator privileges required.
    """

    return await repo_show_an_allocation(id, db, current_user)


@router.get("/get-allocations", response_model=list[ShowAllocations],
            status_code=status.HTTP_202_ACCEPTED)
async def api_get_allocations(
        is_active: Optional[bool] = Query(None,
                                          description="Filter by alloc status"),
        username: Optional[str] = Query(None,
                                        description="Filter by Username"),
        serial_number: Optional[str] = Query(None,
                                             description="Filter by serial Number"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Get All Laptop Allocations**

    Retrieves a list of laptop allocations with optional filters.

    This endpoint allows administrators to view all laptop allocations in the system.
    Results can be filtered based on allocation status, username, or laptop serial number.
    If no filters are provided, all allocations are returned.

    **Query Parameters:**
    - `is_active` (*bool*, optional): Filter allocations by active or inactive status.
    - `username` (*str*, optional): Filter allocations by the username of the assigned user.
    - `serial_number` (*str*, optional): Filter allocations by the laptop's serial number.

    **Responses:**
    - **200 OK:** Returns a list of allocation records matching the provided filters.
      Each record includes related user and laptop details. If no records are found,
      an empty list is returned.
    - **401 Unauthorized:** The requester is not authenticated or not an admin.
    - **422 Unprocessable Entity:** One or more filter parameters are invalid.

    **Authorization:**
    Administrator privileges required.
    """

    return await repo_show_all_allocations(is_active=is_active,
                                           username=username,
                                           serial_number=serial_number, db=db,
                                           admin=current_user)


@router.get("/download-allocation-form", status_code=status.HTTP_202_ACCEPTED)
async def api_download_allocation_form(
        id: uuid.UUID, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
        **Download Allocation Form**

    Downloads the signed laptop allocation form associated with a specific allocation.

    This endpoint allows administrators to retrieve the signed PDF allocation document
    previously uploaded for a given allocation record. The file is returned as a downloadable
    response if it exists in the system.

    **Query Parameters:**
    - `id` (*uuid*, required): The unique identifier of the allocation whose form is to be downloaded.

    **Responses:**
    - **200 OK:** Returns the signed allocation form as a downloadable PDF file.
    - **401 Unauthorized:** The requester is not authenticated or lacks admin privileges.
    - **404 Not Found:** The allocation or associated form does not exist.
    - **422 Unprocessable Entity:** The provided ID format is invalid.

    **Returns:**
    `FileResponse` — The signed allocation form in PDF format.

    **Authorization:**
    Administrator privileges required.



    """
    return await repo_download_form(id=id, db=db, admin=current_user)


@router.get("/download-return-form", status_code=status.HTTP_202_ACCEPTED)
async def api_download_return_form(
        id: uuid.UUID, db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Download Return Form**

    Downloads the signed return form associated with a specific laptop allocation.

    This endpoint retrieves the signed PDF document confirming the return of a laptop.
    If no form has been uploaded, an appropriate error response is returned.
    The file is served as a downloadable attachment.

    **Query Parameters:**
    - `id` (*uuid*, required): The unique identifier of the allocation whose return form is requested.

    **Responses:**
    - **200 OK:** Returns the signed return form as a downloadable PDF.
    - **401 Unauthorized:** The requester is not authenticated.
    - **404 Not Found:** The allocation or associated return form does not exist.

    **Returns:**
    `StreamingResponse` — The signed return form PDF file.

    **Authorization:**
    Requires authentication.
    Administrators and authorized users can download forms for allocations they have access to.
    """

    return await repo_download_return_form(id=id, db=db, admin=current_user)


# ############################################################################################
# --------------------------------- The code below is not final -----------------------------#
# ############################################################################################

@router.get("/generate-form", status_code=status.HTTP_202_ACCEPTED)
async def api_generate_form(
        allocation_id: uuid.UUID, form_type: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    **Generate Form**

    Generates a PDF form (allocation or return) based on the details of a specific laptop allocation.

    This endpoint creates a PDF document using the data associated with a given allocation record.
    The `form_type` parameter determines whether to generate an **allocation** form or a **return** form.
    The generated document can later be signed and uploaded through the appropriate upload endpoint.

    **Query Parameters:**
    - `allocation_id` (*uuid*, required): The unique identifier of the allocation for which the form is generated.
    - `form_type` (*str*, required): Type of form to generate. Accepts `"allocation"` or `"return"`.

    **Responses:**
    - **200 OK:** Returns the generated PDF document.
    - **400 Bad Request:** Invalid or missing `form_type` value.
    - **401 Unauthorized:** The requester is not authenticated.
    - **404 Not Found:** No allocation exists for the provided ID.

    **Returns:**
    `FileResponse` — The generated PDF document ready for download.

    **Authorization:**
    Requires authentication.
    Only administrators are authorized to generate forms.
    """
    org_name = await repo_get_organization_name(db=db, admin=current_user)

    allocation = await repo_show_an_allocation(allocation_id, db, current_user)
    logo = get_logo_path()

    org_config = {
        # "logo_path": "core/assets/logo.png",
        "logo_path": logo,
        "org_name": f"{org_name}",
        "title": f"Laptop {form_type.capitalize()} Form",
        "doc_number": "IT-AL-001",
        "revision": "03",
        "approved_by": "Head of IT",
        "watermark": "CONFIDENTIAL",
    }

    if form_type.lower() == "allocation":
        pdf_bytes = await repo_create_allocation_form(allocation, org_config,
                                                      db)
        alloc_filename = f"{allocation.user.username}_allocation_form.pdf"
    elif form_type.lower() == "return":
        pdf_bytes = await repo_create_return_form(allocation, org_config, db)
        alloc_filename = f"{allocation.user.username}_return_form.pdf"
    else:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The only options are Allocation and Return"
        )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={alloc_filename}"
        }
    )
