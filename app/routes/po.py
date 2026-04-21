from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database.db import get_db
from app.schemas.po import POCreate, POResponse, POListResponse, POStatusUpdate, POListItem, POUpdate
from app.models.po import POStatus
from app.crud import po as crud_po
from app.core.logger import setup_logger

router = APIRouter(prefix="/po", tags=["Purchase Order"])
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
    db: Session = Depends(get_db)
):
    """
    Create a new Purchase Order
    """
    try:
        logger.info(f"API: Create PO request received for vendor: {po_data.vendor_id}")
        po = crud_po.create_po(db, po_data)
        logger.info(f"API: PO created successfully with ID: {po.id}")
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
    db: Session = Depends(get_db)
):
    """
    Get Purchase Order by ID
    """
    try:
        logger.info(f"API: Get PO request received for ID: {po_id}")
        po = crud_po.get_po_by_id(db, po_id)
        
        if not po:
            logger.warning(f"API: PO not found - {po_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PO_NOT_FOUND", "message": "Purchase Order not found"}
            )
        
        logger.info(f"API: PO retrieved successfully: {po_id}")
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
    db: Session = Depends(get_db)
):
    """
    Get all Purchase Orders with pagination and optional status filter
    
    Examples:
    - Get all POs: /po?page=1&limit=10
    - Filter by status: /po?status=draft&page=1&limit=10
    """
    try:
        logger.info(f"API: Get POs request - Status: {status_filter}, Page: {page}, Limit: {limit}")
        
        skip = (page - 1) * limit
        
        if status_filter:
            pos = crud_po.get_pos_by_status(db, status_filter, skip, limit)
            total = crud_po.get_pos_count_by_status(db, status_filter)
        else:
            pos = crud_po.get_all_pos(db, skip, limit)
            total = crud_po.get_pos_count(db)
        
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
        
        logger.info(f"API: Retrieved {len(data)} POs")
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
    db: Session = Depends(get_db)
):
    """
    Update Purchase Order status
    """
    try:
        logger.info(f"API: Update PO status request received - ID: {po_id}, Status: {status_data.status}")
        po = crud_po.update_po_status(db, po_id, status_data.status)
        
        if not po:
            logger.warning(f"API: PO not found for status update - {po_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PO_NOT_FOUND", "message": "Purchase Order not found"}
            )
        
        logger.info(f"API: PO status updated successfully: {po_id} -> {status_data.status}")
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
    description="Search for a specific Purchase Order by its PO number (e.g., PO-001)"
)
async def search_purchase_order(
    po_number: str,
    db: Session = Depends(get_db)
):
    """
    Search Purchase Order by PO Number
    """
    try:
        logger.info(f"API: Search PO request received for number: {po_number}")
        po = crud_po.search_po_by_number(db, po_number)
        
        if not po:
            logger.warning(f"API: PO not found with number - {po_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PO_NOT_FOUND", "message": f"Purchase Order with number {po_number} not found"}
            )
        
        logger.info(f"API: PO retrieved successfully: {po_number}")
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
    db: Session = Depends(get_db)
):
    """
    Update Purchase Order items
    
    Note: Only POs with DRAFT status can be edited
    """
    try:
        logger.info(f"API: Update PO request received for ID: {po_id}")
        po = crud_po.update_po(db, po_id, po_data)
        
        if not po:
            logger.warning(f"API: PO not found - {po_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PO_NOT_FOUND", "message": "Purchase Order not found"}
            )
        
        logger.info(f"API: PO updated successfully: {po_id}")
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
