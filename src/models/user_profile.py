import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID
from src.models.base import Base

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    phone: Mapped[str | None] = mapped_column(sa.String(20))
    address: Mapped[str | None] = mapped_column(sa.Text)
    bio: Mapped[str | None] = mapped_column(sa.Text)

    user: Mapped["UserModel"] = relationship(back_populates="profile")
