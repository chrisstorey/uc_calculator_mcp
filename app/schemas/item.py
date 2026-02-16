"""Item schemas for request/response validation."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ItemBase(BaseModel):
    """Base item schema."""

    title: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    """Item creation schema."""

    owner_id: Optional[int] = None


class ItemUpdate(BaseModel):
    """Item update schema."""

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ItemResponse(ItemBase):
    """Item response schema."""

    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        from_attributes = True
