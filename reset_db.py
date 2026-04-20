from sqlalchemy import text
from app.database.db import engine

# Drop tables manually
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS pr_items CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS purchase_request CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS purchase_order CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS vendors CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS items CASCADE"))
    conn.commit()
    print("✅ Tables dropped")

# Recreate with new schema
from app.database.db import Base
from app.models.pr import PurchaseRequest
from app.models.po import PurchaseOrder
from app.models.vendor import Vendor
from app.models.item_model import Item

Base.metadata.create_all(bind=engine)
print("✅ Tables recreated with new schema")
print("\n📋 Tables created:")
print("   - purchase_request")
print("   - purchase_order (with vendor_name)")
print("   - vendors (with UUID id)")
print("   - items")
