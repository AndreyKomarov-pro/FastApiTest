from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.schemas.product import ProductInCartResponse


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Имя пользователя")

    @field_validator("username", mode="before")
    @classmethod
    def username_not_null(cls, v: object) -> object:
        if v is None:
            raise ValueError("Имя пользователя не может быть null")
        return v


class UserResponse(BaseModel):
    id: UUID
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CartCreate(BaseModel):
    pass


class CartUpdate(BaseModel):
    product_ids: list[UUID] = Field(..., description="Список ID товаров")


class CartResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime | None
    user: UserResponse
    products: list[ProductInCartResponse] = []

    model_config = {"from_attributes": True}
