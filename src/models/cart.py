from uuid import UUID, uuid4
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.models.cart_product import cart_products
from src.models.base import Base


class CartModel(Base):
    __tablename__ = 'carts'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        default=None,
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["UserModel"] = relationship(back_populates="cart")

    products: Mapped[list["ProductModel"]] = relationship(
        "ProductModel",
        secondary=cart_products,
        back_populates="carts",
    )