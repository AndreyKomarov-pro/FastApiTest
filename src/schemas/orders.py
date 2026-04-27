from typing import Optional
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from src.enums.order_status import OrderStatus
from src.schemas.product import ProductInCartResponse
from src.schemas.users import UserResponse


class OrderItemBody(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1, description="Количество товара")


class OrderItemResponse(BaseModel):
    id: UUID
    quantity: int
    price: Decimal
    product: ProductInCartResponse

    model_config = {"from_attributes": True}


class OrderBody(BaseModel):
    user_id: UUID
    item_ids: list[OrderItemBody] = Field(default_factory=list, description="Список товаров")


class OrderCreate(BaseModel):
    body: OrderBody


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None


class OrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]
    user: UserResponse
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}
