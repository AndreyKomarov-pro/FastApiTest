from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ProductInfoBody(BaseModel):
    product_id: UUID
    rating: Decimal
    reviews_count: int
    warehouse_stock: int


class ProductInfoResponse(BaseModel):
    id: UUID
    product_id: UUID
    rating: Decimal
    reviews_count: int
    warehouse_stock: int

    model_config = ConfigDict(from_attributes=True)
