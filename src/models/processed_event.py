from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ProcessedEventModel(Base):
    __tablename__ = "processed_events"

    event_id: Mapped[UUID] = mapped_column(sa.Uuid, nullable=False, unique=True)
    topic: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
