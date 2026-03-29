from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from uuid import UUID

from src.models.cart_product import cart_products
from src.models.base import Base


class CartModel(Base):
    __tablename__ = 'carts'

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        default=None,
        onupdate=func.now(),
    )

    user: Mapped["UserModel"] = relationship(back_populates="cart")
    products: Mapped[list["ProductModel"]] = relationship(
        "ProductModel",
        secondary=cart_products,
        back_populates="carts",
    )
