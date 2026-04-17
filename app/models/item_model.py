from sqlalchemy import Column, String, DateTime, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.database.db import Base
from app.enums.item_enum import ItemType, ItemCategory 


class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)

    item_type = Column(SqlEnum(ItemType), nullable=False)
    item_category = Column(SqlEnum(ItemCategory), nullable=False)

    uom = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}')>"