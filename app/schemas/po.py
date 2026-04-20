from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from app.models.po import POStatus, POType, MatchingType


class POItemCreate(BaseModel):
    item_id: UUID = Field(..., description="Reference to Item Master")
    ordered_qty: int = Field(..., gt=0, description="Ordered quantity")
    unit_price: Decimal = Field(..., gt=0, description="Unit price")
    gst_percent: Decimal = Field(..., ge=0, description="GST percentage")
    cgst_percent: Decimal = Field(..., ge=0, description="CGST percentage")
    sgst_percent: Decimal = Field(..., ge=0, description="SGST percentage")
    igst_percent: Decimal = Field(..., ge=0, description="IGST percentage")
    uom: str = Field(..., description="Unit of measurement")
    hsn_code: str = Field(..., description="HSN code")


class POItemResponse(BaseModel):
    item_id: UUID
    ordered_qty: int
    unit_price: Decimal
    gst_percent: Decimal
    cgst_percent: Decimal
    sgst_percent: Decimal
    igst_percent: Decimal
    uom: str
    hsn_code: str
    
    class Config:
        from_attributes = True


class POCreate(BaseModel):
    pr_id: Optional[UUID] = Field(None, description="Reference to Purchase Request")
    vendor_id: UUID = Field(..., description="Vendor ID")
    store_id: UUID = Field(..., description="Store ID")
    location_id: UUID = Field(..., description="Location ID")
    created_by: UUID = Field(..., description="User who created the PO")
    po_type: POType = Field(..., description="Type of PO")
    matching_type: MatchingType = Field(..., description="Matching type")
    po_date: date = Field(..., description="PO date")
    items: List[POItemCreate] = Field(..., min_length=1, description="List of items in PO")
    
    @field_validator('items')
    @classmethod
    def validate_unique_items(cls, items: List[POItemCreate]) -> List[POItemCreate]:
        item_ids = [item.item_id for item in items]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("Duplicate item_id entries are not allowed in the same PO")
        return items


class POResponse(BaseModel):
    id: UUID
    po_number: str
    pr_id: Optional[UUID]
    vendor_id: UUID
    store_id: UUID
    location_id: UUID
    created_by: UUID
    po_type: POType
    matching_type: MatchingType
    po_date: date
    status: POStatus
    items: List[POItemResponse]
    total_amount: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class POListItem(BaseModel):
    id: UUID
    po_number: str
    pr_id: Optional[UUID]
    vendor_id: UUID
    store_id: UUID
    po_type: POType
    po_date: date
    status: POStatus
    items: List[POItemResponse]
    total_amount: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class POListResponse(BaseModel):
    data: List[POListItem]
    page: int
    limit: int
    total: int


class POStatusUpdate(BaseModel):
    status: POStatus = Field(..., description="New status for the PO")


class POUpdate(BaseModel):
    items: List[POItemCreate] = Field(..., min_length=1, description="Updated list of items in PO")
    
    @field_validator('items')
    @classmethod
    def validate_unique_items(cls, items: List[POItemCreate]) -> List[POItemCreate]:
        item_ids = [item.item_id for item in items]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("Duplicate item_id entries are not allowed in the same PO")
        return items
