from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.pr import PRStatus


class PRItemCreate(BaseModel):
    item_id: UUID = Field(..., description="Reference to Item Master")
    quantity: int = Field(..., gt=0, description="Required quantity must be greater than 0")


class PRItemResponse(BaseModel):
    item_id: UUID
    quantity: int
    
    class Config:
        from_attributes = True


class PRCreate(BaseModel):
    requested_by: str = Field(..., min_length=1, description="User who created the PR")
    items: List[PRItemCreate] = Field(..., min_length=1, description="List of items in PR")
    
    @field_validator('items')
    @classmethod
    def validate_unique_items(cls, items: List[PRItemCreate]) -> List[PRItemCreate]:
        item_ids = [item.item_id for item in items]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("Duplicate item_id entries are not allowed in the same PR")
        return items


class PRResponse(BaseModel):
    id: UUID
    pr_number: str
    requested_by: str
    status: PRStatus
    items: List[PRItemResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PRListItem(BaseModel):
    id: UUID
    pr_number: str
    requested_by: str
    status: PRStatus
    items: List[PRItemResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PRListResponse(BaseModel):
    data: List[PRListItem]
    page: int
    limit: int
    total: int


class PRStatusUpdate(BaseModel):
    status: PRStatus = Field(..., description="New status for the PR")



class PRUpdate(BaseModel):
    items: List[PRItemCreate] = Field(..., min_length=1, description="Updated list of items in PR")
    
    @field_validator('items')
    @classmethod
    def validate_unique_items(cls, items: List[PRItemCreate]) -> List[PRItemCreate]:
        item_ids = [item.item_id for item in items]
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("Duplicate item_id entries are not allowed in the same PR")
        return items
