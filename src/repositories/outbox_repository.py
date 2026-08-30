from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums.outbox_status import OutboxStatus
from src.models.outbox_event import OutboxEventModel
from src.schemas.outbox import OutboxEventToSend


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event: OutboxEventModel) -> OutboxEventModel:
        self.session.add(event)
        await self.session.flush()
        return event

    async def claim_pending(
        self, batch_size: int, processing_timeout: int,
    ) -> list[OutboxEventToSend]:
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(seconds=processing_timeout)

        stmt = (
            select(OutboxEventModel)
            .where(
                sa.or_(
                    sa.and_(
                        OutboxEventModel.status == OutboxStatus.PENDING,
                        sa.or_(
                            OutboxEventModel.next_retry_at.is_(None),
                            OutboxEventModel.next_retry_at <= now,
                        ),
                    ),
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
            event.processing_id = uuid4()

        await self.session.flush()

        return OutboxEventToSend.from_list(events)

    async def mark_sent(self, event_id: UUID, processing_id: UUID) -> bool:
        stmt = (
            update(OutboxEventModel)
            .where(
                OutboxEventModel.id == event_id,
                OutboxEventModel.processing_id == processing_id,
            )
            .values(
                status=OutboxStatus.SENT,
                sent_at=datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def record_failure(
        self,
        event_id: UUID,
        processing_id: UUID,
        status: OutboxStatus,
        next_retry_at: datetime | None,
    ) -> bool:
        stmt = (
            update(OutboxEventModel)
            .where(
                OutboxEventModel.id == event_id,
                OutboxEventModel.processing_id == processing_id,
            )
            .values(
                attempts=OutboxEventModel.attempts + 1,
                last_attempt_at=datetime.now(timezone.utc),
                processing_id=sa.null(),
                status=status,
                next_retry_at=next_retry_at,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
