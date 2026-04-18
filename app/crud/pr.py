from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
from app.models.pr import PurchaseRequest, PRStatus
from app.schemas.pr import PRCreate
import logging

logger = logging.getLogger(__name__)


def generate_pr_number(db: Session) -> str:
    """Generate next PR number in format PR-001, PR-002, etc."""
    try:
        # Get the last PR number
        last_pr = db.query(PurchaseRequest).order_by(PurchaseRequest.created_at.desc()).first()
        
        if last_pr and last_pr.pr_number:
            # Extract number from PR-XXX format
            last_number = int(last_pr.pr_number.split('-')[1])
            next_number = last_number + 1
        else:
            next_number = 1
        
        return f"PR-{next_number:03d}"
    except Exception as e:
        logger.error(f"Error generating PR number: {str(e)}")
        # Fallback to timestamp-based number
        from datetime import datetime
        return f"PR-{int(datetime.utcnow().timestamp())}"


def create_pr(db: Session, pr_data: PRCreate) -> PurchaseRequest:
    """Create a new Purchase Request with items"""
    try:
        logger.info(f"Creating PR for user: {pr_data.requested_by}")
        
        # Generate PR number
        pr_number = generate_pr_number(db)
        
        # Convert items to dict format for JSON storage
        items_data = [
            {
                "item_id": str(item.item_id),
                "quantity": item.quantity
            }
            for item in pr_data.items
        ]
        
        new_pr = PurchaseRequest(
            pr_number=pr_number,
            requested_by=pr_data.requested_by,
            status=PRStatus.DRAFT,
            items=items_data
        )
        
        db.add(new_pr)
        db.commit()
        db.refresh(new_pr)
        
        logger.info(f"PR created successfully with number: {pr_number}, ID: {new_pr.id}")
        return new_pr
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating PR: {str(e)}")
        raise


def get_pr_by_id(db: Session, pr_id: UUID) -> Optional[PurchaseRequest]:
    """Get PR by ID"""
    try:
        logger.info(f"Fetching PR with ID: {pr_id}")
        pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id).first()
        return pr
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching PR: {str(e)}")
        raise


def get_all_prs(db: Session, skip: int = 0, limit: int = 10) -> List[PurchaseRequest]:
    """Get all PRs with pagination"""
    try:
        logger.info(f"Fetching PRs - Skip: {skip}, Limit: {limit}")
        prs = db.query(PurchaseRequest).offset(skip).limit(limit).all()
        return prs
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching PRs: {str(e)}")
        raise


def get_prs_count(db: Session) -> int:
    """Get total count of PRs"""
    try:
        return db.query(PurchaseRequest).count()
    except SQLAlchemyError as e:
        logger.error(f"Database error while counting PRs: {str(e)}")
        raise


def update_pr_status(db: Session, pr_id: UUID, new_status: PRStatus) -> Optional[PurchaseRequest]:
    """Update PR status"""
    try:
        logger.info(f"Updating PR {pr_id} status to {new_status}")
        
        pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id).first()
        
        if pr:
            pr.status = new_status
            db.commit()
            db.refresh(pr)
            logger.info(f"PR status updated successfully: {pr_id} -> {new_status}")
        
        return pr
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating PR status: {str(e)}")
        raise



def search_pr_by_number(db: Session, pr_number: str) -> Optional[PurchaseRequest]:
    """Search PR by PR number"""
    try:
        logger.info(f"Searching PR with number: {pr_number}")
        pr = db.query(PurchaseRequest).filter(PurchaseRequest.pr_number == pr_number).first()
        return pr
    except SQLAlchemyError as e:
        logger.error(f"Database error while searching PR: {str(e)}")
        raise



def update_pr(db: Session, pr_id: UUID, pr_data) -> Optional[PurchaseRequest]:
    """Update PR items (only for draft status)"""
    try:
        logger.info(f"Updating PR {pr_id}")
        
        pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id).first()
        
        if not pr:
            return None
        
        # Check if PR is in draft status
        if pr.status != PRStatus.DRAFT:
            raise ValueError(f"Cannot edit PR with status: {pr.status}. Only DRAFT PRs can be edited.")
        
        # Convert items to dict format for JSON storage
        items_data = [
            {
                "item_id": str(item.item_id),
                "quantity": item.quantity
            }
            for item in pr_data.items
        ]
        
        pr.items = items_data
        db.commit()
        db.refresh(pr)
        
        logger.info(f"PR updated successfully: {pr_id}")
        return pr
        
    except ValueError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating PR: {str(e)}")
        raise



def get_prs_by_status(db: Session, status: PRStatus, skip: int = 0, limit: int = 10) -> List[PurchaseRequest]:
    """Get PRs filtered by status with pagination"""
    try:
        logger.info(f"Fetching PRs with status: {status} - Skip: {skip}, Limit: {limit}")
        prs = db.query(PurchaseRequest).filter(PurchaseRequest.status == status).offset(skip).limit(limit).all()
        return prs
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching PRs by status: {str(e)}")
        raise


def get_prs_count_by_status(db: Session, status: PRStatus) -> int:
    """Get total count of PRs by status"""
    try:
        return db.query(PurchaseRequest).filter(PurchaseRequest.status == status).count()
    except SQLAlchemyError as e:
        logger.error(f"Database error while counting PRs by status: {str(e)}")
        raise
