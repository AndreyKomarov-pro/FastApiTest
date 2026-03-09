from uuid import UUID, uuid4
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from src.models.cart_product import cart_products
from sqlalchemy.orm import relationship
from src.models.base import Base


class ProductModel(Base):
    __tablename__ = 'products'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    price: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer, default=0)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    category: Mapped["CategoryModel"] = relationship(back_populates="products")

    carts: Mapped[list["CartModel"]] = relationship(
        "CartModel",
        secondary=cart_products,
        back_populates="products",
    )