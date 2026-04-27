from typing import Optional
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.schemas.category import CategoryResponse


class ProductBody(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=200,
        description="Название товара",
        json_schema_extra={"examples": ["Товар"]},
    )
    description: Optional[str] = Field(default=None, max_length=2000, description="Описание товара")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Цена товара")
    quantity: int = Field(default=0, ge=0, description="Количество товара")

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Название товара не может быть пустым")
        return stripped

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Цена должна быть больше нуля")
        return v


class ProductCreateBody(BaseModel):
    body: ProductBody


class ProductResponse(BaseModel):
    id: UUID
    body: ProductBody
    created_at: datetime
    category: CategoryResponse

    model_config = {"from_attributes": True}


class ProductInCartResponse(BaseModel):
    id: UUID
    body: ProductBody
    created_at: datetime

    model_config = {"from_attributes": True}
