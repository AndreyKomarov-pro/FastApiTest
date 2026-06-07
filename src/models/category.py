from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class CategoryModel(Base):
    __tablename__ = 'categories'

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    status: Mapped[str] = mapped_column(sa.String(20), nullable=False, default="PENDING")
    idempotency_key: Mapped[UUID | None] = mapped_column(sa.Uuid, nullable=True)
    payload_json: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    next_retry_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(sa.Integer, default=0, server_default=sa.text("0"))
    claimed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    products: Mapped[list["ProductModel"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
