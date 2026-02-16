"""User management endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


# Mock database
users_db = {}


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user."""
    user_id = len(users_db) + 1
    user_data = user.model_dump()
    user_data["id"] = user_id
    users_db[user_id] = user_data
    return user_data


@router.get("/", response_model=List[UserResponse])
async def list_users():
    """List all users."""
    return list(users_db.values())


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get a specific user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate):
    """Update a user."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump()
    user_data["id"] = user_id
    users_db[user_id] = user_data
    return user_data


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return None
