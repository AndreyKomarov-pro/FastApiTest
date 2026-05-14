from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.enums.order_status import OrderStatus
from src.exceptions import ValidationException
from src.models.order import OrderModel
from src.models.order_item import OrderItem

class OrderItemBody(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1)
    price: Decimal = Field(..., gt=0, decimal_places=2)

class OrderBody(BaseModel):
    user_id: UUID
    items: list[OrderItemBody] = Field(default_factory=list)

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list) -> list:
        if not v:
            raise ValidationException(field="items", message="Заказ должен содержать хотя бы один товар")
        return v

    def to_model(self) -> OrderModel:
        order = OrderModel(
            user_id=self.user_id,
            status=OrderStatus.PENDING,
        )
        order.order_items = [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in self.items
        ]
        return order

class OrderCreate(BaseModel):
    body: OrderBody

class OrderUpdateBody(BaseModel):
    status: Optional[OrderStatus] = None

class OrderUpdate(BaseModel):
    body: OrderUpdateBody

class OrderItemResponse(BaseModel):
    id: UUID
    quantity: int
    price: Decimal
    product_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]
    order_items: list[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model: OrderModel) -> "OrderResponse":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models: list[OrderModel]) -> list["OrderResponse"]:
        return [cls.model_validate(m) for m in models]
