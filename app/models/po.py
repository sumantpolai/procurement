import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Date, Enum as SQLEnum, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.database.db import Base


class POStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CLOSED = "closed"


class POType(str, enum.Enum):
    STANDARD = "STANDARD"
    BLANKET = "BLANKET"
    CONTRACT = "CONTRACT"
    PLANNED = "PLANNED"


class MatchingType(str, enum.Enum):
    TWO_WAY = "TWO_WAY"
    THREE_WAY = "THREE_WAY"
    FOUR_WAY = "FOUR_WAY"


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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
