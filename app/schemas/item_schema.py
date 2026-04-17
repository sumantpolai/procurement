from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.enums.item_enum import ItemType, ItemCategory


# -----------------------
# Request Schema
# -----------------------
class ItemCreate(BaseModel):
    name: str
    item_type: ItemType
    item_category: ItemCategory
    uom: str


# -----------------------
# Response Schema
# -----------------------
class ItemResponse(BaseModel):
    id: UUID
    name: str
    item_type: ItemType
    item_category: ItemCategory
    uom: str
    created_at: datetime

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