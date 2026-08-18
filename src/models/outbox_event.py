from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.models.enums.outbox_status import OutboxStatus


class OutboxEventModel(Base):
    __tablename__ = "outbox_events"

    aggregate_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    aggregate_id: Mapped[UUID] = mapped_column(sa.Uuid, nullable=False)
    event_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    topic: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    payload: Mapped[str] = mapped_column(sa.Text, nullable=False)
    status: Mapped[str] = mapped_column(
        sa.String(20), nullable=False, default=OutboxStatus.PENDING,
        server_default=OutboxStatus.PENDING,
    )
    attempts: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, default=0, server_default=sa.text("0"),
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True,
    )
    next_retry_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True,
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True,
    )
