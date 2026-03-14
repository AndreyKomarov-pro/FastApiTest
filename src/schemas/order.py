from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.models.order import OrderStatus
from src.schemas.order_item import OrderItemCreate, OrderItemResponse
from src.schemas.user import UserCreate, UserResponse


class OrderCreate(BaseModel):
    user: UserCreate
    items: list[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None


class OrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime | None
    user: UserResponse
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}
