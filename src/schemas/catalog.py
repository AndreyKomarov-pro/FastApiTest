from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.exceptions.validation import ValidationException


class ProductBody(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = Field(default=None)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    quantity: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValidationException(field="name", message="Название товара не может быть пустым")
        return stripped

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped:
            raise ValidationException(field="description", message="Описание не может быть пустым")
        return stripped

class CategoryBaseBody(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = Field(default=None)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValidationException(field="name", message="Название категории не может быть пустым")
        return stripped

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped:
            raise ValidationException(field="description", message="Описание не может быть пустым")
        return stripped


class CategoryBody(CategoryBaseBody):
    products: list[ProductBody] = Field(default_factory=list)

    @field_validator("products")
    @classmethod
    def validate_products(cls, v: list[ProductBody]) -> list[ProductBody]:
        if not v:
            raise ValidationException(field="products", message="Категория должна содержать хотя бы один товар")
        return v


class CategoryUpdateBody(CategoryBaseBody):
    pass

class CategoryCreate(BaseModel):
    body: CategoryBody

class CategoryUpdate(BaseModel):
    body: CategoryUpdateBody

class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    price: Decimal
    quantity: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    products: list[ProductResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "CategoryResponse":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models) -> list["CategoryResponse"]:
        return [cls.model_validate(m) for m in models]
