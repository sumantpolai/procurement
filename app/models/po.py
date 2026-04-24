import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Date, Enum as SQLEnum, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.database.db import Base
from app.enums.po_enums import POStatus, POType, MatchingType
from app.core.timezone import get_current_time


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_number = Column(String, unique=True, nullable=False, index=True)
    pr_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to PR
    vendor_id = Column(UUID(as_uuid=True), nullable=False)
    vendor_name = Column(String, nullable=True)  # Store vendor name for quick access
    store_id = Column(UUID(as_uuid=True), nullable=False)
    location_id = Column(UUID(as_uuid=True), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    po_type = Column(SQLEnum(POType), nullable=False, default=POType.STANDARD)
    matching_type = Column(SQLEnum(MatchingType), nullable=False, default=MatchingType.THREE_WAY)
    po_date = Column(Date, nullable=False)
    status = Column(SQLEnum(POStatus), nullable=False, default=POStatus.DRAFT)
    items = Column(JSON, nullable=False)  # Store items as JSON array
    total_amount = Column(Numeric(15, 2), nullable=True)  # Calculated total
    created_at = Column(DateTime, default=lambda: get_current_time().replace(tzinfo=None), nullable=False)
    updated_at = Column(DateTime, default=lambda: get_current_time().replace(tzinfo=None), onupdate=lambda: get_current_time().replace(tzinfo=None))
