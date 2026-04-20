from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from datetime import datetime
import enum

from app.database.db import Base


class VendorStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)

    # Bank Details
    bank_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    ifsc_code = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    address = Column(String, nullable=False)

    # Status
    status = Column(Enum(VendorStatus), default=VendorStatus.DRAFT, nullable=False)
    approved_by = Column(String, nullable=True)
    rejected_reason = Column(String, nullable=True)

    # Soft Delete
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)