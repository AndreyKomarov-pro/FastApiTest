import asyncio
import logging

from src.config import settings
from src.database import SessionFactory
from src.infrastructure.kafka.producer import KafkaProducer
from src.models.enums.outbox_status import OutboxStatus
from src.repositories.outbox_repository import OutboxRepository
from src.schemas.outbox import OutboxEventToSend
from src.workers.backoff import calculate_next_retry

logger = logging.getLogger(__name__)


async def outbox_relay(producer: KafkaProducer) -> None:
    logger.info("Outbox relay started")
    semaphore = asyncio.Semaphore(settings.outbox_concurrency)

    while True:
        try:
            async with SessionFactory() as session:
                repo = OutboxRepository(session)
                events = await repo.claim_pending(
                    settings.outbox_batch_size,
                    settings.outbox_processing_timeout,
                )
                await session.commit()

            await asyncio.gather(
                *(_send_event(event, producer, semaphore) for event in events)
            )

        except Exception as exc:
            logger.exception("Outbox relay error: %s", exc)

        await asyncio.sleep(settings.outbox_poll_interval)


async def _send_event(
    event: OutboxEventToSend,
    producer: KafkaProducer,
    semaphore: asyncio.Semaphore,
) -> None:
    async with semaphore:
        try:
            await producer.send(
                topic=event.topic,
                key=str(event.aggregate_id),
                value=event.payload,
            )
        except Exception as exc:
            logger.exception("Failed to send event %s: %s", event.id, exc)
            await _record_failure(event)
            return

        async with SessionFactory() as session:
            repo = OutboxRepository(session)
            is_marked = await repo.mark_sent(event.id, event.processing_id)
            await session.commit()

        if is_marked:
            logger.info("Sent event %s to %s", event.id, event.topic)
        else:
            logger.warning("Event %s was claimed by another worker", event.id)


async def _record_failure(event: OutboxEventToSend) -> None:
    is_final = event.attempts + 1 >= settings.outbox_max_retries
    status = OutboxStatus.FAILED if is_final else OutboxStatus.PENDING
    next_retry_at = None if is_final else calculate_next_retry(
        event.attempts,
        settings.outbox_base_backoff,
        settings.outbox_max_backoff,
    )

    async with SessionFactory() as session:
        repo = OutboxRepository(session)
        is_recorded = await repo.record_failure(
            event.id, event.processing_id, status, next_retry_at,
        )
        await session.commit()

    if not is_recorded:
        logger.warning("Event %s was claimed by another worker", event.id)
    elif is_final:
        logger.warning("Event %s reached max retries, marked FAILED", event.id)
