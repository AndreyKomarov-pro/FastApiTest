from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID

from src.models.base import Base


class ProductModel(Base):
    __tablename__ = 'products'

    name: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer, default=0)
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )

    category: Mapped["CategoryModel"] = relationship(back_populates="products")
