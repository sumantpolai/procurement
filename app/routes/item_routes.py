from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.item_schema import ItemUpdate

from app.database.db import get_db
from app.crud.item_crud import ItemCRUD
from app.schemas.item_schema import (
    ItemCreate,
    ItemResponse,
    ItemListResponse
)

router = APIRouter(prefix="/api/items", tags=["Items"])


# -----------------------
# Create Item
# -----------------------
@router.post("/", response_model=ItemResponse, status_code=201)
def create_item_api(
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    try:
        crud = ItemCRUD(db)
        return crud.create_item(item)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create item: {str(e)}"
        )


# -----------------------
# Get All Items
# -----------------------
@router.get("/", response_model=ItemListResponse)
def get_all_items_api(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    try:
        crud = ItemCRUD(db)
        return crud.get_items(page, limit)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch items: {str(e)}"
        )


# -----------------------
# Search Items
# -----------------------
@router.get("/search/", response_model=list[ItemResponse])
def search_items_api(
    name: str,
    db: Session = Depends(get_db)
):
    try:
        crud = ItemCRUD(db)
        return crud.search_items(name)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
        
        
        
# -----------------------
# Update Item
# -----------------------
@router.put("/{item_id}", response_model=ItemResponse)
def update_item_api(
    item_id: UUID,
    item: ItemUpdate,
    db: Session = Depends(get_db)
):
    try:
        crud = ItemCRUD(db)
        updated_item = crud.update_item(item_id, item)

        if not updated_item:
            raise HTTPException(status_code=404, detail="Item not found")

        return updated_item

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update item: {str(e)}"
        )
        
        
# -----------------------
# Delete Item
# -----------------------
@router.delete("/{item_id}")
def delete_item_api(
    item_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        crud = ItemCRUD(db)
        success = crud.delete_item(item_id)

        if not success:
            raise HTTPException(status_code=404, detail="Item not found")

        return {"message": "Item deleted successfully"}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete item: {str(e)}"
        )