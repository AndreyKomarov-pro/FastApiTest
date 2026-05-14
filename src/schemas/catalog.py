from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.exceptions import ValidationException
from src.models.category import CategoryModel
from src.models.product import ProductModel

class ProductBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
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
        return stripped or None

class CategoryBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None)
    products: list[ProductBody] = Field(default_factory=list)

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
        return stripped or None

    def to_model(self) -> CategoryModel:
        category = CategoryModel(name=self.name, description=self.description)
        category.products = [
            ProductModel(
                name=p.name,
                description=p.description,
                price=p.price,
                quantity=p.quantity,
            )
            for p in self.products
        ]
        return category

class CategoryCreate(BaseModel):
    body: CategoryBody

class CategoryUpdateBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
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
        return stripped or None

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
    def from_model(cls, model: CategoryModel) -> "CategoryResponse":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models: list[CategoryModel]) -> list["CategoryResponse"]:
        return [cls.model_validate(m) for m in models]
