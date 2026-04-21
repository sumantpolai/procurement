import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.database.db import Base


class PRStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class PurchaseRequest(Base):
    __tablename__ = "purchase_request"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pr_number = Column(String, unique=True, nullable=False, index=True)
    requested_by = Column(String, nullable=False)
    status = Column(SQLEnum(PRStatus), nullable=False, default=PRStatus.DRAFT)
    items = Column(JSON, nullable=False)  # Store items as JSON array
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
