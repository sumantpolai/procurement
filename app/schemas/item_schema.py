from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.enums.item_enum import ItemStatus, ItemType, ItemCategory


# -----------------------
# Request Schema
# -----------------------
class ItemCreate(BaseModel):
    name: str
    item_type: ItemType
    item_category: ItemCategory
    uom: str
    created_by: str
    status: ItemStatus = ItemStatus.DRAFT
    rejection_reason: Optional[str] = None


# -----------------------
# Response Schema
# -----------------------
class ItemResponse(BaseModel):
    id: UUID
    code: str
    name: str
    item_type: ItemType
    item_category: ItemCategory
    uom: str
    status: ItemStatus
    rejection_reason: Optional[str]
    created_by: str 
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True   # for SQLAlchemy ORM


# -----------------------
# Paginated Response
# -----------------------
class ItemListResponse(BaseModel):
    data: list[ItemResponse]
    page: int
    limit: int
    total: int
    
    
# -----------------------
# Update Item
# -----------------------
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    item_type: Optional[ItemType] = None
    item_category: Optional[ItemCategory] = None
    uom: Optional[str] = None
    status: Optional[ItemStatus] = None
    rejection_reason: Optional[str] = None