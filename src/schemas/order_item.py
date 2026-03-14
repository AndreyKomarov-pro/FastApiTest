from pydantic import BaseModel
from uuid import UUID
from src.schemas.product import ProductCreate, ProductResponse


class OrderItemCreate(BaseModel):
    product: ProductCreate
    quantity: int = 1


class OrderItemUpdate(BaseModel):
    quantity: int | None = None


class OrderItemResponse(BaseModel):
    id: UUID
    quantity: int
    price: float
    product: ProductResponse

    model_config = {"from_attributes": True}
