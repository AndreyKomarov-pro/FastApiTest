from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.exceptions.validation import ValidationException
from src.models.category import CategoryModel
from src.models.product import ProductModel


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

    def to_model(self) -> ProductModel:
        return ProductModel(
            name=self.name,
            description=self.description,
            price=self.price,
            quantity=self.quantity,
        )

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

    def to_model(self, status: str, idempotency_key: UUID) -> CategoryModel:
        category = CategoryModel(
            name=self.name,
            description=self.description,
            status=status,
            idempotency_key=idempotency_key,
        )
        category.products = [p.to_model() for p in self.products]
        return category


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


class EnrichedProductResponse(ProductResponse):
    rating: Decimal | None = None
    reviews_count: int | None = None
    warehouse_stock: int | None = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    created_at: datetime
    products: list[ProductResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> "CategoryResponse":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models) -> list["CategoryResponse"]:
        return [cls.model_validate(m) for m in models]


class EnrichedCategoryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    products: list[EnrichedProductResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model, product_infos: dict) -> "EnrichedCategoryResponse":
        enriched_products = []
        for p in model.products:
            info = product_infos.get(str(p.id))
            enriched_products.append(
                EnrichedProductResponse(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    price=p.price,
                    quantity=p.quantity,
                    created_at=p.created_at,
                    rating=info.rating if info else None,
                    reviews_count=info.reviews_count if info else None,
                    warehouse_stock=info.warehouse_stock if info else None,
                )
            )
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            products=enriched_products,
        )
