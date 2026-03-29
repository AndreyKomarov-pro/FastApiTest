import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class CategoryModel(Base):
    __tablename__ = 'categories'

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)

    products: Mapped[list["ProductModel"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
