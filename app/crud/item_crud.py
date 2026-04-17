from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from app.models.item_model import Item
from app.schemas.item_schema import ItemCreate


class ItemCRUD:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------
    # Create Item
    # -----------------------
    def create_item(self, item_data: ItemCreate) -> Item:

        item = Item(
            name=item_data.name,
            item_type=item_data.item_type,
            item_category=item_data.item_category,
            uom=item_data.uom,
            created_by=item_data.created_by
        )
        
        if item_data.status is not None:
            item.status = item_data.status

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    # -----------------------
    # Get All Items
    # -----------------------
    def get_items(self, page: int = 1, limit: int = 10):

        offset = (page - 1) * limit

        query = self.db.query(Item)

        total = query.count()

        items = (
            query.order_by(Item.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "data": items,
            "page": page,
            "limit": limit,
            "total": total
        }

    # -----------------------
    # Search Items
    # -----------------------
    def search_items(self, name: str):

        return (
            self.db.query(Item)
            .filter(func.lower(Item.name).like(f"%{name.lower()}%"))
            .order_by(Item.name.asc())
            .all()
        )
        
        
    # -----------------------
    # Update Item
    # -----------------------
    def update_item(self, item_id: UUID, item_data) -> Item | None:

        item = self.db.query(Item).filter(Item.id == item_id).first()

        if not item:
            return None

        if item_data.name is not None:
            item.name = item_data.name

        if item_data.item_type is not None:
            item.item_type = item_data.item_type

        if item_data.item_category is not None:
            item.item_category = item_data.item_category

        if item_data.uom is not None:
            item.uom = item_data.uom
            
        if item_data.status is not None:
            item.status = item_data.status

        # ✅ enforce rule
        if item_data.status == "Rejected" and not item_data.rejection_reason:
            raise ValueError("Rejection reason is required when status is Rejected")

        if item_data.rejection_reason is not None:
            item.rejection_reason = item_data.rejection_reason

        self.db.commit()
        self.db.refresh(item)

        return item




    # -----------------------
    # Delete Item
    # -----------------------
    def delete_item(self, item_id: UUID) -> bool:

        item = self.db.query(Item).filter(Item.id == item_id).first()

        if not item:
            return False

        self.db.delete(item)
        self.db.commit()

        return True