from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.database.db import get_db
from app.models.vendor import Vendor

from app.schemas.vendor import (
    VendorCreate, VendorResponse, VendorUpdate,
    VendorStatusUpdate, BankDetails
)

from app.crud.vendor import (
    create_vendor, get_vendors, get_vendor_by_id,
    update_vendor, delete_vendor
)

router = APIRouter()


# 🔹 Helper (mapping DB → response)
def map_vendor(v):
    return VendorResponse(
        id=v.id,
        name=v.name,
        email=v.email,
        phone=v.phone,
        status=v.status,
        bank_details=BankDetails(
            bank_name=v.bank_name,
            account_number=v.account_number,
            ifsc_code=v.ifsc_code,
            branch=v.branch,
            address=v.address
        ),
        created_at=v.created_at
    )


# 🔹 CREATE
@router.post("/", response_model=VendorResponse)
def create_vendor_api(vendor: VendorCreate, db: Session = Depends(get_db)):
    try:
        v = create_vendor(db, vendor)
        return map_vendor(v)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


# 🔹 GET ALL
@router.get("/", response_model=list[VendorResponse])
def get_all_vendors_api(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    vendors = get_vendors(db, skip, limit)
    return [map_vendor(v) for v in vendors]



#search by name  or email
@router.get("/search", response_model=list[VendorResponse])
def search_vendor_api(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    if not search:
        raise HTTPException(status_code=400, detail="Provide search value")

    query = db.query(Vendor).filter(
        Vendor.is_active == True,
        (
            func.lower(Vendor.name).like(f"%{search.lower()}%") |
            func.lower(Vendor.email).like(f"%{search.lower()}%")
        )
    )

    skip = (page - 1) * limit
    vendors = query.offset(skip).limit(limit).all()

    return [map_vendor(v) for v in vendors]

# 🔹 GET BY ID
@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor_api(vendor_id: int, db: Session = Depends(get_db)):
    vendor = get_vendor_by_id(db, vendor_id)

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return map_vendor(vendor)


# 🔹 UPDATE
@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor_api(vendor_id: int, vendor: VendorUpdate, db: Session = Depends(get_db)):
    updated = update_vendor(db, vendor_id, vendor)

    if not updated:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return map_vendor(updated)


# 🔹 DELETE (SOFT)
@router.delete("/{vendor_id}")
def delete_vendor_api(vendor_id: int, db: Session = Depends(get_db)):
    deleted = delete_vendor(db, vendor_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return {"message": "Vendor deleted successfully"}


# 🔹 STATUS UPDATE
from app.models.vendor import VendorStatus

@router.patch("/{vendor_id}/status")
def update_status_api(
    vendor_id: int,
    status_data: VendorStatusUpdate,
    db: Session = Depends(get_db)
):
    vendor = get_vendor_by_id(db, vendor_id)

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Validate status
    if status_data.status not in [e.value for e in VendorStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")

    if status_data.status == "approved":
        if not status_data.approved_by:
            raise HTTPException(status_code=400, detail="approved_by required")

        vendor.approved_by = status_data.approved_by
        vendor.rejected_reason = None

    elif status_data.status == "rejected":
        if not status_data.rejected_reason:
            raise HTTPException(status_code=400, detail="rejected_reason required")

        vendor.rejected_reason = status_data.rejected_reason
        vendor.approved_by = None

    vendor.status = status_data.status

    db.commit()
    db.refresh(vendor)

    return {"message": "Status updated"}