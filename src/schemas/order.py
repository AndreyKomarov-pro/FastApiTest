from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.enums.order_status import OrderStatus
from src.exceptions.validation import ValidationException
from src.models.order import OrderModel
from src.models.order_item import OrderEntryModel

class OrderEntryBody(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1)
    price: Decimal = Field(..., gt=0, decimal_places=2)

class OrderBody(BaseModel):
    user_id: UUID
    items: list[OrderEntryBody] = Field(default_factory=list)

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[OrderEntryBody]) -> list[OrderEntryBody]:
        if not v:
            raise ValidationException(field="items", message="Заказ должен содержать хотя бы один товар")
        return v

    def to_model(self) -> OrderModel:
        order = OrderModel(
            user_id=self.user_id,
            status=OrderStatus.PENDING,
        )
        order.order_items = [
            OrderEntryModel(
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
    status: OrderStatus | None = None

class OrderUpdate(BaseModel):
    body: OrderUpdateBody

class OrderEntryResponse(BaseModel):
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
    updated_at: datetime | None
    order_items: list[OrderEntryResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model: OrderModel) -> "OrderResponse":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models: list[OrderModel]) -> list["OrderResponse"]:
        return [cls.model_validate(m) for m in models]
