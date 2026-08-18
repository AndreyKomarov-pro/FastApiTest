import asyncio
import logging

from src.clients.kafka_producer import KafkaProducer
from src.config import settings
from src.database import SessionFactory
from src.repositories.outbox_repository import OutboxRepository

logger = logging.getLogger(__name__)


async def outbox_relay(producer: KafkaProducer) -> None:
    logger.info("Outbox relay started")

    while True:
        try:
            async with SessionFactory() as session:
                repo = OutboxRepository(session)
                events = await repo.claim_pending(
                    settings.outbox_batch_size,
                    settings.outbox_processing_timeout,
                )
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
                    logger.info("Sent event %s to %s", event.id, event.topic)
                except Exception as exc:
                    logger.error("Failed to send event %s: %s", event.id, exc)
                    async with SessionFactory() as session:
                        repo = OutboxRepository(session)
                        is_final = await repo.record_failure(
                            event.id,
                            settings.outbox_max_retries,
                            settings.outbox_base_backoff,
                            settings.outbox_max_backoff,
                        )
                        await session.commit()
                    if is_final:
                        logger.warning(
                            "Event %s reached max retries, marked FAILED",
                            event.id,
                        )

        except Exception as exc:
            logger.exception("Outbox relay error: %s", exc)

        await asyncio.sleep(settings.outbox_poll_interval)
