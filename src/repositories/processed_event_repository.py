from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.processed_event import ProcessedEventModel


class ProcessedEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_if_not_exists(self, event: ProcessedEventModel) -> bool:
        stmt = (
            insert(ProcessedEventModel)
            .values(
                event_id=event.event_id,
                topic=event.topic,
                event_type=event.event_type,
            )
            .on_conflict_do_nothing(index_elements=["event_id"])
            .returning(ProcessedEventModel.id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
