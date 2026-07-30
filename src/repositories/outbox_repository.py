from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
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

    async def claim_pending(self, batch_size: int) -> list[OutboxEventModel]:
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.status == OutboxStatus.PENDING)
            .order_by(OutboxEventModel.created_at)
            .with_for_update(skip_locked=True)
            .limit(batch_size)
        )
        result = await self.session.execute(stmt)
        events = list(result.scalars().all())

        now = datetime.now(timezone.utc)
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

    async def record_failure(self, event_id: UUID, max_retries: int) -> None:
        stmt = select(OutboxEventModel).where(OutboxEventModel.id == event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one()

        event.attempts += 1
        event.last_attempt_at = datetime.now(timezone.utc)

        if event.attempts >= max_retries:
            event.status = OutboxStatus.FAILED
        else:
            event.status = OutboxStatus.PENDING
