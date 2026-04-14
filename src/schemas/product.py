from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.schemas.category import CategoryResponse


class ProductCreateBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    quantity: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    quantity: int = Field(default=0, ge=0)
    category_id: UUID

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    quantity: int | None = Field(default=None, ge=0)
    category_id: UUID | None = None

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip()
        return v


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    price: Decimal
    quantity: int
    created_at: datetime
    category: CategoryResponse

    model_config = {"from_attributes": True}


class ProductInCartResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    price: Decimal
    quantity: int
    created_at: datetime

    model_config = {"from_attributes": True}
