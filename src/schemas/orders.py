from typing import Optional
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from src.enums.order_status import OrderStatus
from src.schemas.product import ProductInCartResponse
from src.schemas.users import UserResponse


class OrderItemProductRef(BaseModel):
    product_id: UUID


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1, description="Количество товара")


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, ge=1, description="Количество товара")
    product: Optional[OrderItemProductRef] = None


class OrderItemResponse(BaseModel):
    id: UUID
    quantity: int
    price: Decimal
    product: ProductInCartResponse

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    user_id: UUID
    item_ids: list[OrderItemCreate] = Field(default_factory=list, description="Список товаров")


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
