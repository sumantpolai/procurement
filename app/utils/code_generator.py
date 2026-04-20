from sqlalchemy.orm import Session
from app.models.item_model import Item


def generate_item_code(db: Session) -> str:
    last_item = db.query(Item).order_by(Item.created_at.desc()).first()

    if not last_item:
        return "ITM-0001"

    try:
        last_number = int(last_item.code.split("-")[1])
    except:
        last_number = 0

    new_number = last_number + 1

    return f"ITM-{new_number:04d}" 