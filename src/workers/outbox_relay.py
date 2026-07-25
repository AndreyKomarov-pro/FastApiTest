import asyncio
import logging

from src.config import Settings
from src.database import SessionFactory
from src.kafka.producer import KafkaProducer
from src.repositories.outbox_repository import OutboxRepository

logger = logging.getLogger(__name__)

settings = Settings()


async def outbox_relay(producer: KafkaProducer) -> None:
    logger.info("Outbox relay started")

    while True:
        try:
            async with SessionFactory() as session:
                repo = OutboxRepository(session)
                events = await repo.claim_unsent(settings.outbox_batch_size)
                await session.commit()

            for event in events:
                try:
                    await producer.send(
                        topic=event.topic,
                        key=str(event.aggregate_id),
                        value=event.payload,
                    )
                    async with SessionFactory() as session:
                        repo = OutboxRepository(session)
                        await repo.mark_sent(event.id)
                        await session.commit()
                    logger.info("Sent outbox event %s to topic %s", event.id, event.topic)
                except Exception as exc:
                    logger.error("Failed to send event %s: %s", event.id, exc)

        except Exception as exc:
            logger.error("Outbox relay error: %s", exc)

        await asyncio.sleep(settings.outbox_poll_interval)
