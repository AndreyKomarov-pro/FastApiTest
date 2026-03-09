from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.models.order import OrderStatus
from src.schemas.order_item import OrderItemResponse, OrderItemCreate
from src.schemas.user import UserResponse


class OrderCreate(BaseModel):
    user_id: UUID
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True