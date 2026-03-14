from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from src.models.base import Base


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    orders: Mapped[list["OrderModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    cart: Mapped["CartModel"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
