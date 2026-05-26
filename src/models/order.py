import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID
from src.models.base import Base
from src.enums.order_status import OrderStatus

class OrderModel(Base):
    __tablename__ = 'orders'

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        sa.String(20),
        default=OrderStatus.PENDING,
    )

    user: Mapped["UserModel"] = relationship(back_populates="orders")

    order_entries: Mapped[list["OrderEntryModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
