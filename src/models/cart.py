from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID

from src.models.cart_product import cart_products
from src.models.base import Base, UUIDMixin, CreatedAtMixin, UpdatedAtMixin


class CartModel(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = 'carts'

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    user: Mapped["UserModel"] = relationship(back_populates="cart")
    products: Mapped[list["ProductModel"]] = relationship(
        "ProductModel",
        secondary=cart_products,
        back_populates="carts",
    )
