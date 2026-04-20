from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.db import Base

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # FK to Item
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)