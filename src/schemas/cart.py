from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.schemas.user import UserCreate, UserResponse
from src.schemas.product import ProductResponse


class CartCreate(BaseModel):
    user: UserCreate


class CartResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    products: list[ProductResponse] = []

    model_config = {"from_attributes": True}
