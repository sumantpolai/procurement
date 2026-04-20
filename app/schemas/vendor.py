from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


# 🔹 Bank Details
class BankDetails(BaseModel):
    bank_name: str
    account_number: str
    ifsc_code: str
    branch: str
    address: str


# 🔹 Create
class VendorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    
    pan_no: str
    gst_no: Optional[str] = None

    bank_name: str
    account_number: str
    ifsc_code: str
    branch: str
    address: str


# 🔹 Update
class VendorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    
    pan_no: Optional[str] = None
    gst_no: Optional[str] = None

    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch: Optional[str] = None
    address: Optional[str] = None


# 🔹 Status Update
class VendorStatusUpdate(BaseModel):
    status: str
    approved_by: Optional[str] = None
    rejected_reason: Optional[str] = None


# 🔹 Response
class VendorResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    status: str
    
    pan_no: str
    gst_no: Optional[str] = None

    bank_details: BankDetails

    created_at: datetime

    class Config:
        from_attributes = True