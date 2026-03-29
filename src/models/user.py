from sqlalchemy.orm import Mapped, relationship

from src.models.base import Base


class UserModel(Base):
    __tablename__ = 'users'

    username: Mapped[str]

    orders: Mapped[list["OrderModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    cart: Mapped["CartModel"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
