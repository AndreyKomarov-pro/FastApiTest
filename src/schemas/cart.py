from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.schemas.user import UserResponse
from src.schemas.product import ProductResponse


class CartCreate(BaseModel):
    user_id: UUID


class CartResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    products: list[ProductResponse] = []

    class Config:
        from_attributes = True