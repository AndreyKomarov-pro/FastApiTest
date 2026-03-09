from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.schemas.category import CategoryResponse


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    quantity: int = 0
    category_id: UUID


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    price: float
    quantity: int
    created_at: datetime
    category: CategoryResponse

    class Config:
        from_attributes = True