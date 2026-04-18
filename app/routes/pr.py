from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database.db import get_db
from app.schemas.pr import PRCreate, PRResponse, PRListResponse, PRStatusUpdate, PRListItem, PRUpdate
from app.models.pr import PRStatus
from app.crud import pr as crud_pr
from app.core.logger import setup_logger

router = APIRouter(prefix="/pr", tags=["Purchase Request"])
logger = setup_logger(__name__)


@router.post(
    "",
    response_model=PRResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Purchase Request",
    description="Create a new Purchase Request with items"
)
async def create_purchase_request(
    pr_data: PRCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new Purchase Request
    
    - **requested_by**: User who created the PR (required)
    - **items**: List of items with item_id and quantity (required, min 1 item)
    """
    try:
        logger.info(f"API: Create PR request received for user: {pr_data.requested_by}")
        pr = crud_pr.create_pr(db, pr_data)
        logger.info(f"API: PR created successfully with ID: {pr.id}")
        return pr
    except Exception as e:
        logger.error(f"API: Failed to create PR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to create Purchase Request"}
        )


@router.get(
    "/{pr_id}",
    response_model=PRResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Purchase Request by ID",
    description="Retrieve a specific Purchase Request by its ID"
)
async def get_purchase_request(
    pr_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get Purchase Request by ID
    
    - **pr_id**: UUID of the Purchase Request
    """
    try:
        logger.info(f"API: Get PR request received for ID: {pr_id}")
        pr = crud_pr.get_pr_by_id(db, pr_id)
        
        if not pr:
            logger.warning(f"API: PR not found - {pr_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PR_NOT_FOUND", "message": "Purchase Request not found"}
            )
        
        logger.info(f"API: PR retrieved successfully: {pr_id}")
        return pr
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to fetch PR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to fetch Purchase Request"}
        )


@router.get(
    "",
    response_model=PRListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get All Purchase Requests",
    description="Retrieve all Purchase Requests with pagination and optional status filter"
)
async def get_all_purchase_requests(
    status_filter: Optional[PRStatus] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get all Purchase Requests with pagination and optional status filter
    
    - **status**: Optional filter by status (draft, submitted, approved, rejected)
    - **page**: Page number (default: 1)
    - **limit**: Records per page (default: 10)
    
    Examples:
    - Get all PRs: /pr?page=1&limit=10
    - Filter by status: /pr?status=draft&page=1&limit=10
    """
    try:
        logger.info(f"API: Get PRs request - Status: {status_filter}, Page: {page}, Limit: {limit}")
        
        skip = (page - 1) * limit
        
        if status_filter:
            prs = crud_pr.get_prs_by_status(db, status_filter, skip, limit)
            total = crud_pr.get_prs_count_by_status(db, status_filter)
        else:
            prs = crud_pr.get_all_prs(db, skip, limit)
            total = crud_pr.get_prs_count(db)
        
        data = [
            PRListItem(
                id=pr.id,
                pr_number=pr.pr_number,
                requested_by=pr.requested_by,
                status=pr.status,
                items=pr.items,
                created_at=pr.created_at,
                updated_at=pr.updated_at
            )
            for pr in prs
        ]
        
        logger.info(f"API: Retrieved {len(data)} PRs")
        return PRListResponse(data=data, page=page, limit=limit, total=total)
        
    except Exception as e:
        logger.error(f"API: Failed to fetch PRs - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to fetch Purchase Requests"}
        )


@router.patch(
    "/{pr_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Update Purchase Request Status",
    description="Update the status of a Purchase Request"
)
async def update_purchase_request_status(
    pr_id: UUID,
    status_data: PRStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update Purchase Request status
    
    - **pr_id**: UUID of the Purchase Request
    - **status**: New status (draft, submitted, approved, rejected)
    """
    try:
        logger.info(f"API: Update PR status request received - ID: {pr_id}, Status: {status_data.status}")
        pr = crud_pr.update_pr_status(db, pr_id, status_data.status)
        
        if not pr:
            logger.warning(f"API: PR not found for status update - {pr_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PR_NOT_FOUND", "message": "Purchase Request not found"}
            )
        
        logger.info(f"API: PR status updated successfully: {pr_id} -> {status_data.status}")
        return {"message": "PR status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to update PR status - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to update Purchase Request status"}
        )



@router.get(
    "/search/{pr_number}",
    response_model=PRResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Purchase Request by PR Number",
    description="Search for a specific Purchase Request by its PR number (e.g., PR-001)"
)
async def search_purchase_request(
    pr_number: str,
    db: Session = Depends(get_db)
):
    """
    Search Purchase Request by PR Number
    
    - **pr_number**: PR number in format PR-XXX (e.g., PR-001, PR-002)
    """
    try:
        logger.info(f"API: Search PR request received for number: {pr_number}")
        pr = crud_pr.search_pr_by_number(db, pr_number)
        
        if not pr:
            logger.warning(f"API: PR not found with number - {pr_number}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PR_NOT_FOUND", "message": f"Purchase Request with number {pr_number} not found"}
            )
        
        logger.info(f"API: PR retrieved successfully: {pr_number}")
        return pr
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to search PR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to search Purchase Request"}
        )



@router.put(
    "/{pr_id}",
    response_model=PRResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Purchase Request",
    description="Update PR items (only for DRAFT status PRs)"
)
async def update_purchase_request(
    pr_id: UUID,
    pr_data: PRUpdate,
    db: Session = Depends(get_db)
):
    """
    Update Purchase Request items
    
    - **pr_id**: UUID of the Purchase Request
    - **items**: Updated list of items with item_id and quantity
    
    Note: Only PRs with DRAFT status can be edited
    """
    try:
        logger.info(f"API: Update PR request received for ID: {pr_id}")
        pr = crud_pr.update_pr(db, pr_id, pr_data)
        
        if not pr:
            logger.warning(f"API: PR not found - {pr_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PR_NOT_FOUND", "message": "Purchase Request not found"}
            )
        
        logger.info(f"API: PR updated successfully: {pr_id}")
        return pr
        
    except ValueError as e:
        logger.warning(f"API: Cannot edit PR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_STATUS", "message": str(e)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to update PR - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DATABASE_ERROR", "message": "Failed to update Purchase Request"}
        )
