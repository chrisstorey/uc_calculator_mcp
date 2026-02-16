"""Item management endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter()


# Mock database
items_db = {}


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item."""
    item_id = len(items_db) + 1
    item_data = item.model_dump()
    item_data["id"] = item_id
    items_db[item_id] = item_data
    return item_data


@router.get("/", response_model=List[ItemResponse])
async def list_items():
    """List all items."""
    return list(items_db.values())


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get a specific item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemCreate):
    """Update an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    item_data = item.model_dump()
    item_data["id"] = item_id
    items_db[item_id] = item_data
    return item_data


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return None
