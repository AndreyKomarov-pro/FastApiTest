from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.outbox_event import OutboxEventModel


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event: OutboxEventModel) -> OutboxEventModel:
        self.session.add(event)
        await self.session.flush()
        return event

    async def claim_unsent(self, batch_size: int) -> list[OutboxEventModel]:
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.sent_at.is_(None))
            .order_by(OutboxEventModel.created_at)
            .with_for_update(skip_locked=True)
            .limit(batch_size)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_sent(self, event_id: UUID) -> None:
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(sent_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
