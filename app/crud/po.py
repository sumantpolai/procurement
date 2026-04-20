from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.models.po import PurchaseOrder, POStatus
from app.schemas.po import POCreate
import logging

logger = logging.getLogger(__name__)


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


def calculate_total_amount(items: List[dict]) -> Decimal:
    """Calculate total amount including taxes"""
    total = Decimal('0')
    for item in items:
        qty = Decimal(str(item['ordered_qty']))
        price = Decimal(str(item['unit_price']))
        gst = Decimal(str(item['gst_percent']))
        
        item_total = qty * price
        tax_amount = item_total * (gst / Decimal('100'))
        total += item_total + tax_amount
    
    return round(total, 2)


def create_po(db: Session, po_data: POCreate) -> PurchaseOrder:
    """Create a new Purchase Order with items"""
    try:
        logger.info(f"Creating PO for vendor: {po_data.vendor_id}")
        
        po_number = generate_po_number(db)
        
        items_data = [
            {
                "item_id": str(item.item_id),
                "ordered_qty": item.ordered_qty,
                "unit_price": str(item.unit_price),
                "gst_percent": str(item.gst_percent),
                "cgst_percent": str(item.cgst_percent),
                "sgst_percent": str(item.sgst_percent),
                "igst_percent": str(item.igst_percent),
                "uom": item.uom,
                "hsn_code": item.hsn_code
            }
            for item in po_data.items
        ]
        
        total_amount = calculate_total_amount(items_data)
        
        new_po = PurchaseOrder(
            po_number=po_number,
            pr_id=po_data.pr_id,
            vendor_id=po_data.vendor_id,
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
        
        logger.info(f"PO created successfully with number: {po_number}, ID: {new_po.id}")
        return new_po
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating PO: {str(e)}")
        raise


def get_po_by_id(db: Session, po_id: UUID) -> Optional[PurchaseOrder]:
    """Get PO by ID"""
    try:
        logger.info(f"Fetching PO with ID: {po_id}")
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        return po
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching PO: {str(e)}")
        raise


def get_all_pos(db: Session, skip: int = 0, limit: int = 10) -> List[PurchaseOrder]:
    """Get all POs with pagination"""
    try:
        logger.info(f"Fetching POs - Skip: {skip}, Limit: {limit}")
        pos = db.query(PurchaseOrder).offset(skip).limit(limit).all()
        return pos
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching POs: {str(e)}")
        raise


def get_pos_count(db: Session) -> int:
    """Get total count of POs"""
    try:
        return db.query(PurchaseOrder).count()
    except SQLAlchemyError as e:
        logger.error(f"Database error while counting POs: {str(e)}")
        raise


def update_po_status(db: Session, po_id: UUID, new_status: POStatus) -> Optional[PurchaseOrder]:
    """Update PO status"""
    try:
        logger.info(f"Updating PO {po_id} status to {new_status}")
        
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        
        if po:
            po.status = new_status
            db.commit()
            db.refresh(po)
            logger.info(f"PO status updated successfully: {po_id} -> {new_status}")
        
        return po
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating PO status: {str(e)}")
        raise


def search_po_by_number(db: Session, po_number: str) -> Optional[PurchaseOrder]:
    """Search PO by PO number"""
    try:
        logger.info(f"Searching PO with number: {po_number}")
        po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_number).first()
        return po
    except SQLAlchemyError as e:
        logger.error(f"Database error while searching PO: {str(e)}")
        raise


def update_po(db: Session, po_id: UUID, po_data) -> Optional[PurchaseOrder]:
    """Update PO items (only for draft status)"""
    try:
        logger.info(f"Updating PO {po_id}")
        
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        
        if not po:
            return None
        
        if po.status != POStatus.DRAFT:
            raise ValueError(f"Cannot edit PO with status: {po.status}. Only DRAFT POs can be edited.")
        
        items_data = [
            {
                "item_id": str(item.item_id),
                "ordered_qty": item.ordered_qty,
                "unit_price": str(item.unit_price),
                "gst_percent": str(item.gst_percent),
                "cgst_percent": str(item.cgst_percent),
                "sgst_percent": str(item.sgst_percent),
                "igst_percent": str(item.igst_percent),
                "uom": item.uom,
                "hsn_code": item.hsn_code
            }
            for item in po_data.items
        ]
        
        total_amount = calculate_total_amount(items_data)
        
        po.items = items_data
        po.total_amount = total_amount
        db.commit()
        db.refresh(po)
        
        logger.info(f"PO updated successfully: {po_id}")
        return po
        
    except ValueError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating PO: {str(e)}")
        raise


def get_pos_by_status(db: Session, status: POStatus, skip: int = 0, limit: int = 10) -> List[PurchaseOrder]:
    """Get POs filtered by status with pagination"""
    try:
        logger.info(f"Fetching POs with status: {status} - Skip: {skip}, Limit: {limit}")
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.status == status).offset(skip).limit(limit).all()
        return pos
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching POs by status: {str(e)}")
        raise


def get_pos_count_by_status(db: Session, status: POStatus) -> int:
    """Get total count of POs by status"""
    try:
        return db.query(PurchaseOrder).filter(PurchaseOrder.status == status).count()
    except SQLAlchemyError as e:
        logger.error(f"Database error while counting POs by status: {str(e)}")
        raise
