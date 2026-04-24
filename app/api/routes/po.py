from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database.db import get_db
from app.schemas.po import POCreate, POResponse, POListResponse, POStatusUpdate, POListItem, POUpdate
from app.enums.po_enums import POStatus
from app.models.user import User
from app.crud.po_crud import POCRUD
from app.core.logger import setup_logger
from app.core.timezone import get_current_time
from app.core.dependencies import (
    po_read_access,
    po_create_update_access,
    po_status_update_access
)

router = APIRouter(prefix="/pos", tags=["Purchase Order"])
logger = setup_logger(__name__)


@router.post(
    "",
    response_model=POResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Purchase Order",
    description="Create a new Purchase Order with items"
)
async def create_purchase_order(
    po_data: POCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(po_create_update_access)
):
    """
    Create a new Purchase Order
    """
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Create PO request received for vendor: {po_data.vendor_id}")
        po = POCRUD.create(db, po_data)
        logger.info(f"[{current_time}] API: PO created successfully with ID: {po.id}")
        return po
    except ValueError as e:
        logger.error(f"API: Validation error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "VALIDATION_ERROR", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"API: Failed to create PO - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to create Purchase Order"}
        )


@router.get(
    "/{po_id}",
    response_model=POResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Purchase Order by ID",
    description="Retrieve a specific Purchase Order by its ID"
)
async def get_purchase_order(
    po_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(po_read_access)
):
    """
    Get Purchase Order by ID
    """
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Get PO request received for ID: {po_id}")
        po = POCRUD.get_by_id(db, po_id)
        
        if not po:
            logger.warning(f"API: PO not found - {po_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PO_NOT_FOUND", "message": "Purchase Order not found"}
            )
        
        logger.info(f"[{current_time}] API: PO retrieved successfully: {po_id}")
        return po
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to fetch PO - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to fetch Purchase Order"}
        )


@router.get(
    "",
    response_model=POListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Purchase Orders",
    description="Retrieve all Purchase Orders with pagination and optional status filter"
)
async def get_all_purchase_orders(
    status_filter: Optional[POStatus] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(po_read_access)
):
    """
    Get all Purchase Orders with pagination and optional status filter
    
    Examples:
    - Get all POs: /po?page=1&limit=10
    - Filter by status: /po?status=draft&page=1&limit=10
    """
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Get POs request - Status: {status_filter}, Page: {page}, Limit: {limit}")
        
        skip = (page - 1) * limit
        
        if status_filter:
            pos = POCRUD.get_by_status(db, status_filter, skip, limit)
            total = POCRUD.get_count_by_status(db, status_filter)
        else:
            pos = POCRUD.get_all(db, skip, limit)
            total = POCRUD.get_count(db)
        
        data = [
            POListItem(
                id=po.id,
                po_number=po.po_number,
                pr_id=po.pr_id,
                vendor_id=po.vendor_id,
                vendor_name=po.vendor_name,
                store_id=po.store_id,
                po_type=po.po_type,
                po_date=po.po_date,
                status=po.status,
                items=po.items,
                total_amount=po.total_amount,
                created_at=po.created_at,
                updated_at=po.updated_at
            )
            for po in pos
        ]
        
        logger.info(f"[{current_time}] API: Retrieved {len(data)} POs")
        return POListResponse(data=data, page=page, limit=limit, total=total)
        
    except Exception as e:
        logger.error(f"API: Failed to fetch POs - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to fetch Purchase Orders"}
        )


@router.patch(
    "/{po_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Update Purchase Order Status",
    description="Update the status of a Purchase Order"
)
async def update_purchase_order_status(
    po_id: UUID,
    status_data: POStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(po_status_update_access)
):
    """
    Update Purchase Order status
    """
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Update PO status request received - ID: {po_id}, Status: {status_data.status}")
        po = POCRUD.update_status(db, po_id, status_data.status)
        
        if not po:
            logger.warning(f"API: PO not found for status update - {po_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PO_NOT_FOUND", "message": "Purchase Order not found"}
            )
        
        logger.info(f"[{current_time}] API: PO status updated successfully: {po_id} -> {status_data.status}")
        return {"message": "PO status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to update PO status - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to update Purchase Order status"}
        )


@router.get(
    "/search/{po_number}",
    response_model=POResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Purchase Order by PO Number",
    description="Search for a specific Purchase Order by its PO number"
)
async def search_purchase_order(
    po_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(po_read_access)
):
    """
    Search Purchase Order by PO Number
    """
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Search PO request received for number: {po_number}")
        po = POCRUD.search_by_number(db, po_number)
        
        if not po:
            logger.warning(f"API: PO not found with number - {po_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PO_NOT_FOUND", "message": f"Purchase Order with number {po_number} not found"}
            )
        
        logger.info(f"[{current_time}] API: PO retrieved successfully: {po_number}")
        return po
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to search PO - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to search Purchase Order"}
        )


@router.put(
    "/{po_id}",
    response_model=POResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Purchase Order",
    description="Update PO items (only for DRAFT status POs)"
)
async def update_purchase_order(
    po_id: UUID,
    po_data: POUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(po_create_update_access)
):
    """
    Update Purchase Order items
    
    Note: Only POs with DRAFT status can be edited
    """
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Update PO request received for ID: {po_id}")
        po = POCRUD.update(db, po_id, po_data)
        
        if not po:
            logger.warning(f"API: PO not found - {po_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PO_NOT_FOUND", "message": "Purchase Order not found"}
            )
        
        logger.info(f"[{current_time}] API: PO updated successfully: {po_id}")
        return po
        
    except ValueError as e:
        logger.warning(f"API: Cannot edit PO - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_STATUS", "message": str(e)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to update PO - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to update Purchase Order"}
        )
