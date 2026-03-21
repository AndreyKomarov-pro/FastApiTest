from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID
from enum import Enum

from src.models.base import Base, UUIDMixin, CreatedAtMixin, UpdatedAtMixin


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderModel(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = 'orders'

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(sa.String(20), default=OrderStatus.PENDING)
    total_amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), default=Decimal("0"))
    is_deleted: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
