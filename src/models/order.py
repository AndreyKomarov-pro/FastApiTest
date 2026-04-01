from decimal import Decimal
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from uuid import UUID

from src.models.base import Base
from src.enums.order_status import OrderStatus


class OrderModel(Base):
    __tablename__ = 'orders'

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(sa.String(20), default=OrderStatus.PENDING)
    total_amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), default=Decimal("0"))
    is_deleted: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        default=None,
        onupdate=func.now(),
    )

    user: Mapped["UserModel"] = relationship(back_populates="orders")
    items: Mapped[list["OrderLineModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
