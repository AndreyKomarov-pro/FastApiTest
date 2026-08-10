import asyncio
import json
import logging

from src.config import settings
from src.database import SessionFactory
from src.clients.kafka_producer import KafkaProducer
from src.models.outbox_event import OutboxEventModel
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

            if events:
                async with SessionFactory() as session:
                    repo = OutboxRepository(session)
                    for event in events:
                        try:
                            await producer.send(
                                topic=event.topic,
                                key=str(event.aggregate_id),
                                value=event.payload,
                            )
                            await repo.mark_sent(event.id)
                            logger.info("Sent event %s to %s", event.id, event.topic)
                        except Exception as exc:
                            logger.error("Failed to send event %s: %s", event.id, exc)
                            is_final = await repo.record_failure(
                                event.id, settings.outbox_max_retries,
                            )
                            if is_final:
                                await _send_to_dlq(producer, event, str(exc))
                    await session.commit()

        except Exception as exc:
            logger.exception("Outbox relay error: %s", exc)

        await asyncio.sleep(settings.outbox_poll_interval)


async def _send_to_dlq(
    producer: KafkaProducer, event: OutboxEventModel, error_msg: str | None,
) -> None:
    dlq_payload = json.dumps({
        "original_topic": event.topic,
        "aggregate_type": event.aggregate_type,
        "aggregate_id": str(event.aggregate_id),
        "event_type": event.event_type,
        "payload": event.payload,
        "error": error_msg,
        "attempts": event.attempts,
    })
    await producer.send(
        topic=settings.kafka_topic_dlq,
        key=str(event.aggregate_id),
        value=dlq_payload,
    )
    logger.warning("Event %s sent to DLQ", event.id)
