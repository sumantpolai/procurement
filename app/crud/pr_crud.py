from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
from app.models.pr import PurchaseRequest
from app.enums.pr_enums import PRStatus
from app.schemas.pr import PRCreate, PRUpdate
from app.core.timezone import get_current_time
import logging

logger = logging.getLogger(__name__)


class PRCRUD:
    """Class-based CRUD operations for Purchase Request"""
    
    @staticmethod
    def generate_pr_number(db: Session) -> str:
        """Generate next PR number in format PR-001, PR-002, etc."""
        try:
            last_pr = db.query(PurchaseRequest).order_by(PurchaseRequest.created_at.desc()).first()
            
            if last_pr and last_pr.pr_number:
                last_number = int(last_pr.pr_number.split('-')[1])
                next_number = last_number + 1
            else:
                next_number = 1
            
            return f"PR-{next_number:03d}"
        except Exception as e:
            logger.error(f"Error generating PR number: {str(e)}")
            from datetime import datetime
            return f"PR-{int(datetime.utcnow().timestamp())}"
    
    @staticmethod
    def create(db: Session, pr_data: PRCreate) -> PurchaseRequest:
        """Create a new Purchase Request with items"""
        try:
            current_time = get_current_time()
            logger.info(f"[{current_time}] Creating PR for user: {pr_data.requested_by}")
            
            pr_number = PRCRUD.generate_pr_number(db)
            
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
            
            logger.info(f"[{current_time}] PR created successfully with number: {pr_number}, ID: {new_pr.id}")
            return new_pr
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating PR: {str(e)}")
            raise
    
    @staticmethod
    def get_by_id(db: Session, pr_id: UUID) -> Optional[PurchaseRequest]:
        """Get PR by ID"""
        try:
            logger.info(f"Fetching PR with ID: {pr_id}")
            return db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching PR: {str(e)}")
            raise
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 10) -> List[PurchaseRequest]:
        """Get all PRs with pagination"""
        try:
            logger.info(f"Fetching PRs - Skip: {skip}, Limit: {limit}")
            return db.query(PurchaseRequest).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching PRs: {str(e)}")
            raise
    
    @staticmethod
    def get_count(db: Session) -> int:
        """Get total count of PRs"""
        try:
            return db.query(PurchaseRequest).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error while counting PRs: {str(e)}")
            raise
    
    @staticmethod
    def update_status(db: Session, pr_id: UUID, new_status: PRStatus) -> Optional[PurchaseRequest]:
        """Update PR status"""
        try:
            current_time = get_current_time()
            logger.info(f"[{current_time}] Updating PR {pr_id} status to {new_status}")
            
            pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id).first()
            
            if pr:
                pr.status = new_status
                db.commit()
                db.refresh(pr)
                logger.info(f"[{current_time}] PR status updated successfully: {pr_id} -> {new_status}")
            
            return pr
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while updating PR status: {str(e)}")
            raise
    
    @staticmethod
    def search_by_number(db: Session, pr_number: str) -> Optional[PurchaseRequest]:
        """Search PR by PR number"""
        try:
            logger.info(f"Searching PR with number: {pr_number}")
            return db.query(PurchaseRequest).filter(PurchaseRequest.pr_number == pr_number).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while searching PR: {str(e)}")
            raise
    
    @staticmethod
    def update(db: Session, pr_id: UUID, pr_data: PRUpdate) -> Optional[PurchaseRequest]:
        """Update PR items (only for draft status)"""
        try:
            current_time = get_current_time()
            logger.info(f"[{current_time}] Updating PR {pr_id}")
            
            pr = db.query(PurchaseRequest).filter(PurchaseRequest.id == pr_id).first()
            
            if not pr:
                return None
            
            if pr.status != PRStatus.DRAFT:
                raise ValueError(f"Cannot edit PR with status: {pr.status}. Only DRAFT PRs can be edited.")
            
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
            
            logger.info(f"[{current_time}] PR updated successfully: {pr_id}")
            return pr
            
        except ValueError:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while updating PR: {str(e)}")
            raise
    
    @staticmethod
    def get_by_status(db: Session, status: PRStatus, skip: int = 0, limit: int = 10) -> List[PurchaseRequest]:
        """Get PRs filtered by status with pagination"""
        try:
            logger.info(f"Fetching PRs with status: {status} - Skip: {skip}, Limit: {limit}")
            return db.query(PurchaseRequest).filter(PurchaseRequest.status == status).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching PRs by status: {str(e)}")
            raise
    
    @staticmethod
    def get_count_by_status(db: Session, status: PRStatus) -> int:
        """Get total count of PRs by status"""
        try:
            return db.query(PurchaseRequest).filter(PurchaseRequest.status == status).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error while counting PRs by status: {str(e)}")
            raise


# Create instance
pr_crud = PRCRUD()