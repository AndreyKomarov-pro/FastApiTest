import sqlalchemy as sa
from uuid import UUID

from src.models.base import Base

cart_products = sa.Table(
    "cart_products",
    Base.metadata,
    sa.Column("cart_id", sa.ForeignKey("carts.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("product_id", sa.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
)