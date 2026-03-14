from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.schemas.category import CategoryCreate, CategoryResponse


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    quantity: int = 0
    category: CategoryCreate


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None
    category: CategoryCreate | None = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    price: float
    quantity: int
    created_at: datetime
    category: CategoryResponse

    model_config = {"from_attributes": True}
