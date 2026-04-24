from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
from app.models.po import PurchaseOrder
from app.enums.po_enums import POStatus
from app.schemas.po import POCreate, POUpdate
from app.core.timezone import get_current_time
import logging

logger = logging.getLogger(__name__)


class POCRUD:
    """Class-based CRUD operations for Purchase Order"""
    
    @staticmethod
    def generate_po_number(db: Session) -> str:
        """Generate next PO number in format PO-001, PO-002, etc."""
        try:
            last_po = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).first()
            
            if last_po and last_po.po_number:
                last_number = int(last_po.po_number.split('-')[1])
                next_number = last_number + 1
            else:
                next_number = 1
            
            return f"PO-{next_number:03d}"
        except Exception as e:
            logger.error(f"Error generating PO number: {str(e)}")
            from datetime import datetime
            return f"PO-{int(datetime.utcnow().timestamp())}"
    
    @staticmethod
    def create(db: Session, po_data: POCreate) -> PurchaseOrder:
        """Create a new Purchase Order with items"""
        try:
            current_time = get_current_time()
            logger.info(f"[{current_time}] Creating PO for vendor: {po_data.vendor_id}")
            
            po_number = POCRUD.generate_po_number(db)
            
            items_data = [
                {
                    "item_id": str(item.item_id),
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "total_price": float(item.quantity * item.unit_price)
                }
                for item in po_data.items
            ]
            
            total_amount = sum(item["total_price"] for item in items_data)
            
            new_po = PurchaseOrder(
                po_number=po_number,
                pr_id=po_data.pr_id,
                vendor_id=po_data.vendor_id,
                vendor_name=po_data.vendor_name,
                store_id=po_data.store_id,
                location_id=po_data.location_id,
                created_by=po_data.created_by,
                po_type=po_data.po_type,
                matching_type=po_data.matching_type,
                po_date=po_data.po_date,
                status=POStatus.DRAFT,
                items=items_data,
                total_amount=total_amount
            )
            
            db.add(new_po)
            db.commit()
            db.refresh(new_po)
            
            logger.info(f"[{current_time}] PO created successfully with number: {po_number}, ID: {new_po.id}")
            return new_po
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating PO: {str(e)}")
            raise
    
    @staticmethod
    def get_by_id(db: Session, po_id: UUID) -> Optional[PurchaseOrder]:
        """Get PO by ID"""
        try:
            logger.info(f"Fetching PO with ID: {po_id}")
            return db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching PO: {str(e)}")
            raise
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 10) -> List[PurchaseOrder]:
        """Get all POs with pagination"""
        try:
            logger.info(f"Fetching POs - Skip: {skip}, Limit: {limit}")
            return db.query(PurchaseOrder).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching POs: {str(e)}")
            raise
    
    @staticmethod
    def get_count(db: Session) -> int:
        """Get total count of POs"""
        try:
            return db.query(PurchaseOrder).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error while counting POs: {str(e)}")
            raise
    
    @staticmethod
    def update_status(db: Session, po_id: UUID, new_status: POStatus) -> Optional[PurchaseOrder]:
        """Update PO status"""
        try:
            current_time = get_current_time()
            logger.info(f"[{current_time}] Updating PO {po_id} status to {new_status}")
            
            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
            
            if po:
                po.status = new_status
                db.commit()
                db.refresh(po)
                logger.info(f"[{current_time}] PO status updated successfully: {po_id} -> {new_status}")
            
            return po
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while updating PO status: {str(e)}")
            raise
    
    @staticmethod
    def search_by_number(db: Session, po_number: str) -> Optional[PurchaseOrder]:
        """Search PO by PO number"""
        try:
            logger.info(f"Searching PO with number: {po_number}")
            return db.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_number).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while searching PO: {str(e)}")
            raise
    
    @staticmethod
    def update(db: Session, po_id: UUID, po_data: POUpdate) -> Optional[PurchaseOrder]:
        """Update PO items (only for draft status)"""
        try:
            current_time = get_current_time()
            logger.info(f"[{current_time}] Updating PO {po_id}")
            
            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
            
            if not po:
                return None
            
            if po.status != POStatus.DRAFT:
                raise ValueError(f"Cannot edit PO with status: {po.status}. Only DRAFT POs can be edited.")
            
            items_data = [
                {
                    "item_id": str(item.item_id),
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "total_price": float(item.quantity * item.unit_price)
                }
                for item in po_data.items
            ]
            
            total_amount = sum(item["total_price"] for item in items_data)
            
            po.items = items_data
            po.total_amount = total_amount
            db.commit()
            db.refresh(po)
            
            logger.info(f"[{current_time}] PO updated successfully: {po_id}")
            return po
            
        except ValueError:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while updating PO: {str(e)}")
            raise
    
    @staticmethod
    def get_by_status(db: Session, status: POStatus, skip: int = 0, limit: int = 10) -> List[PurchaseOrder]:
        """Get POs filtered by status with pagination"""
        try:
            logger.info(f"Fetching POs with status: {status} - Skip: {skip}, Limit: {limit}")
            return db.query(PurchaseOrder).filter(PurchaseOrder.status == status).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching POs by status: {str(e)}")
            raise
    
    @staticmethod
    def get_count_by_status(db: Session, status: POStatus) -> int:
        """Get total count of POs by status"""
        try:
            return db.query(PurchaseOrder).filter(PurchaseOrder.status == status).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error while counting POs by status: {str(e)}")
            raise


# Create instance
po_crud = POCRUD()
