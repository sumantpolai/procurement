# from sqlalchemy.orm import Session
# from app.models.vendor import Vendor


# def create_vendor(db: Session, vendor):
#     db_vendor = Vendor(**vendor.dict())
#     db.add(db_vendor)
#     db.commit()
#     db.refresh(db_vendor)
#     return db_vendor


# def get_vendors(db: Session, skip: int = 0, limit: int = 10):
#     return db.query(Vendor).filter(Vendor.is_active == True).offset(skip).limit(limit).all()


# def get_vendor_by_id(db: Session, vendor_id: int):
#     return db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.is_active == True).first()


# def update_vendor(db: Session, vendor_id: int, vendor_data):
#     vendor = get_vendor_by_id(db, vendor_id)

#     if not vendor:
#         return None

#     for key, value in vendor_data.dict(exclude_unset=True).items():
#         setattr(vendor, key, value)

#     db.commit()
#     db.refresh(vendor)
#     return vendor


# def delete_vendor(db: Session, vendor_id: int):
#     vendor = get_vendor_by_id(db, vendor_id)

#     if not vendor:
#         return None

#     vendor.is_active = False
#     db.commit()
#     return vendor


# def search_vendors(db: Session, search: str):
#     return db.query(Vendor).filter(
#         Vendor.is_active == True,
#         (Vendor.name.ilike(f"%{search}%") | Vendor.email.ilike(f"%{search}%"))
#     ).all()
from sqlalchemy.orm import Session
from app.models.vendor import Vendor


def create_vendor(db: Session, vendor):
    db_vendor = Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


def get_vendors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Vendor).filter(Vendor.is_active == True).offset(skip).limit(limit).all()


def get_vendor_by_id(db: Session, vendor_id: int):
    return db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.is_active == True).first()


def update_vendor(db: Session, vendor_id: int, vendor_data):
    vendor = get_vendor_by_id(db, vendor_id)

    if not vendor:
        return None

    for key, value in vendor_data.dict(exclude_unset=True).items():
        setattr(vendor, key, value)

    db.commit()
    db.refresh(vendor)
    return vendor


def delete_vendor(db: Session, vendor_id: int):
    vendor = get_vendor_by_id(db, vendor_id)

    if not vendor:
        return None

    vendor.is_active = False
    db.commit()
    return vendor


def search_vendors(db: Session, search: str):
    return db.query(Vendor).filter(
        Vendor.is_active == True,
        (Vendor.name.ilike(f"%{search}%") | Vendor.email.ilike(f"%{search}%"))
    ).all()