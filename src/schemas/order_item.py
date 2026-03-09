from pydantic import BaseModel
from uuid import UUID
from src.schemas.product import ProductResponse


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = 1


class OrderItemResponse(BaseModel):
    id: UUID
    quantity: int
    price: float
    product: ProductResponse

    class Config:
        from_attributes = True