from sqlalchemy import text

def generate_item_code(db):
    result = db.execute(text("SELECT nextval('item_code_seq')"))
    next_val = result.scalar()
    return f"ITM-{next_val:04d}"