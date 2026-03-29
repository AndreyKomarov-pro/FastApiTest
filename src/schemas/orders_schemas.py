from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from src.enums.order_status import OrderStatus
from src.schemas.catalog_schemas import ProductResponse
from src.schemas.users_schemas import UserResponse


class OrderItemProductRef(BaseModel):
    product_id: UUID


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1)


class OrderItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=1)
    product: OrderItemProductRef | None = None


class OrderItemResponse(BaseModel):
    id: UUID
    quantity: int
    price: Decimal
    product: ProductResponse

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    user_id: UUID
    item_ids: list[OrderItemCreate] = Field(default_factory=list)


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None


class OrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime | None
    user: UserResponse
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}
