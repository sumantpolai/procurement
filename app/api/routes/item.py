from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.db import get_db
from app.crud.item_crud import ItemCRUD
from app.schemas.item_schema import (
    ItemCreate,
    ItemResponse,
    ItemListResponse,
    ItemUpdate
)
from app.core.logger import setup_logger
from app.core.timezone import get_current_time

router = APIRouter(prefix="/items", tags=["Items"])
logger = setup_logger(__name__)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item_api(
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    """Create a new item"""
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Create item request received: {item.name}")
        crud = ItemCRUD(db)
        result = crud.create_item(item)
        logger.info(f"[{current_time}] API: Item created successfully: {result.id}")
        return result
    except Exception as e:
        logger.error(f"API: Failed to create item - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create item: {str(e)}"
        )


@router.get("/", response_model=ItemListResponse)
def get_all_items_api(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    """Get all items with pagination"""
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Get items request - Page: {page}, Limit: {limit}")
        crud = ItemCRUD(db)
        result = crud.get_items(page, limit)
        logger.info(f"[{current_time}] API: Retrieved {len(result['data'])} items")
        return result
    except Exception as e:
        logger.error(f"API: Failed to fetch items - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch items: {str(e)}"
        )


@router.get("/search/", response_model=list[ItemResponse])
def search_items_api(
    name: str,
    db: Session = Depends(get_db)
):
    """Search items by name"""
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Search items request for: {name}")
        crud = ItemCRUD(db)
        result = crud.search_items(name)
        logger.info(f"[{current_time}] API: Found {len(result)} items matching '{name}'")
        return result
    except Exception as e:
        logger.error(f"API: Search failed - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.put("/{item_id}", response_model=ItemResponse)
def update_item_api(
    item_id: UUID,
    item: ItemUpdate,
    db: Session = Depends(get_db)
):
    """Update an item"""
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Update item request for ID: {item_id}")
        crud = ItemCRUD(db)
        updated_item = crud.update_item(item_id, item)

        if not updated_item:
            logger.warning(f"API: Item not found - {item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        logger.info(f"[{current_time}] API: Item updated successfully: {item_id}")
        return updated_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to update item - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update item: {str(e)}"
        )


@router.delete("/{item_id}")
def delete_item_api(
    item_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an item"""
    try:
        current_time = get_current_time()
        logger.info(f"[{current_time}] API: Delete item request for ID: {item_id}")
        crud = ItemCRUD(db)
        success = crud.delete_item(item_id)

        if not success:
            logger.warning(f"API: Item not found - {item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        logger.info(f"[{current_time}] API: Item deleted successfully: {item_id}")
        return {"message": "Item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to delete item - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete item: {str(e)}"
        )
