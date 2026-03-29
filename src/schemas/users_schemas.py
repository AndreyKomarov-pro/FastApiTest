from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.catalog_schemas import ProductResponse


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: UUID
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CartCreate(BaseModel):
    user_id: UUID
    product_ids: list[UUID] = []


class CartResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime | None
    user: UserResponse
    products: list[ProductResponse] = []

    model_config = {"from_attributes": True}
