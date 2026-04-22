from typing import Optional
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.schemas.category import CategoryResponse


class ProductCreateBody(BaseModel):
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
    def name_strip(cls, v: str) -> str:
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


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    description: Optional[str] = Field(default=None, max_length=2000, description="Описание товара")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Цена товара")
    quantity: int = Field(default=0, ge=0, description="Количество товара")
    category_id: UUID

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Название товара не может быть пустым")
        return stripped


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Название товара")
    description: Optional[str] = Field(default=None, max_length=2000, description="Описание товара")
    price: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2, description="Цена товара")
    quantity: Optional[int] = Field(default=None, ge=0, description="Количество товара")
    category_id: Optional[UUID] = None

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Название товара не может быть пустым")
            return stripped
        return v

    @field_validator("name", "price", "quantity", mode="before")
    @classmethod
    def not_null(cls, v: object) -> object:
        if v is None:
            raise ValueError("Поле не может быть null")
        return v


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    quantity: int
    created_at: datetime
    category: CategoryResponse

    model_config = {"from_attributes": True}


class ProductInCartResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    quantity: int
    created_at: datetime

    model_config = {"from_attributes": True}
