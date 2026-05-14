from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base

class UserModel(Base):
    __tablename__ = 'users'

    username: Mapped[str]
    email: Mapped[str]
    full_name: Mapped[str | None]

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    orders: Mapped[list["OrderModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
