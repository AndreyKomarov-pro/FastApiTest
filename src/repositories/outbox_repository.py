from datetime import datetime, timedelta, timezone
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select, update, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums.outbox_status import OutboxStatus
from src.models.outbox_event import OutboxEventModel


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event: OutboxEventModel) -> OutboxEventModel:
        self.session.add(event)
        await self.session.flush()
        return event

    async def claim_pending(
        self, batch_size: int, processing_timeout: int,
    ) -> list[OutboxEventModel]:
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(seconds=processing_timeout)

        stmt = (
            select(OutboxEventModel)
            .where(
                sa.or_(
                    OutboxEventModel.status == OutboxStatus.PENDING,
                    sa.and_(
                        OutboxEventModel.status == OutboxStatus.PROCESSING,
                        OutboxEventModel.last_attempt_at < stale_threshold,
                    ),
                )
            )
            .order_by(OutboxEventModel.created_at)
            .with_for_update(skip_locked=True)
            .limit(batch_size)
        )
        result = await self.session.execute(stmt)
        events = list(result.scalars().all())

        for event in events:
            event.status = OutboxStatus.PROCESSING
            event.last_attempt_at = now

        return events

    async def mark_sent(self, event_id: UUID) -> None:
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                status=OutboxStatus.SENT,
                sent_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)

    async def record_failure(self, event_id: UUID, max_retries: int) -> bool:
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                attempts=OutboxEventModel.attempts + 1,
                last_attempt_at=datetime.now(timezone.utc),
                status=case(
                    (OutboxEventModel.attempts + 1 >= max_retries, OutboxStatus.FAILED),
                    else_=OutboxStatus.PENDING,
                ),
            )
            .returning(OutboxEventModel.attempts)
        )
        result = await self.session.execute(stmt)
        new_attempts = result.scalar_one()
        return new_attempts >= max_retries
