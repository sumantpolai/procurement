from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
from app.models.pr import PurchaseRequest, PRItem, PRStatus
from app.schemas.pr import PRCreate, PRResponse, PRListItem, PRListResponse
from app.utils.exceptions import PRNotFoundException, DatabaseException
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PRService:
    
    @staticmethod
    def create_pr(db: Session, pr_data: PRCreate) -> PurchaseRequest:
        """
        Create a new Purchase Request with items
        """
        try:
            logger.info(f"Creating PR for user: {pr_data.requested_by}")
            
            # Create PR
            new_pr = PurchaseRequest(
                requested_by=pr_data.requested_by,
                status=PRStatus.DRAFT
            )
            
            # Add items
            for item_data in pr_data.items:
                pr_item = PRItem(
                    item_id=item_data.item_id,
                    quantity=item_data.quantity
                )
                new_pr.items.append(pr_item)
            
            db.add(new_pr)
            db.commit()
            db.refresh(new_pr)
            
            logger.info(f"PR created successfully with ID: {new_pr.id}")
            return new_pr
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating PR: {str(e)}")
            raise DatabaseException("Failed to create Purchase Request")
    
    @staticmethod
    def get_pr_by_id(db: Session, pr_id: UUID) -> PurchaseRequest:
        """
        Get PR by ID
        """
        try:
            logger.info(f"Fetching PR with ID: {pr_id}")
            
            pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id).first()
            
            if not pr:
                logger.warning(f"PR not found with ID: {pr_id}")
                raise PRNotFoundException(str(pr_id))
            
            logger.info(f"PR fetched successfully: {pr_id}")
            return pr
            
        except PRNotFoundException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching PR: {str(e)}")
            raise DatabaseException("Failed to fetch Purchase Request")
    
    @staticmethod
    def get_all_prs(db: Session, page: int = 1, limit: int = 10) -> PRListResponse:
        """
        Get all PRs with pagination
        """
        try:
            logger.info(f"Fetching PRs - Page: {page}, Limit: {limit}")
            
            offset = (page - 1) * limit
            
            # Get total count
            total = db.query(PurchaseRequest).count()
            
            # Get paginated results
            prs = db.query(PurchaseRequest).offset(offset).limit(limit).all()
            
            # Transform to list items
            data = [
                PRListItem(
                    id=pr.id,
                    requested_by=pr.requested_by,
                    status=pr.status,
                    total_items=len(pr.items),
                    created_at=pr.created_at
                )
                for pr in prs
            ]
            
            logger.info(f"Fetched {len(data)} PRs out of {total} total")
            
            return PRListResponse(
                data=data,
                page=page,
                limit=limit,
                total=total
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching PRs: {str(e)}")
            raise DatabaseException("Failed to fetch Purchase Requests")
    
    @staticmethod
    def update_pr_status(db: Session, pr_id: UUID, new_status: PRStatus) -> PurchaseRequest:
        """
        Update PR status
        """
        try:
            logger.info(f"Updating PR {pr_id} status to {new_status}")
            
            pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id).first()
            
            if not pr:
                logger.warning(f"PR not found with ID: {pr_id}")
                raise PRNotFoundException(str(pr_id))
            
            pr.status = new_status
            db.commit()
            db.refresh(pr)
            
            logger.info(f"PR status updated successfully: {pr_id} -> {new_status}")
            return pr
            
        except PRNotFoundException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while updating PR status: {str(e)}")
            raise DatabaseException("Failed to update Purchase Request status")
