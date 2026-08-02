import asyncio
import json
import logging

from aiokafka.errors import KafkaError

from src.config import settings
from src.database import SessionFactory
from src.clients.kafka_producer import KafkaProducer
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
                futures = []
                for event in events:
                    try:
                        fut = await producer.send(
                            topic=event.topic,
                            key=str(event.aggregate_id),
                            value=event.payload,
                        )
                        futures.append((event, fut))
                    except KafkaError as exc:
                        logger.error("Failed to queue event %s: %s", event.id, exc)
                        futures.append((event, exc))

                await producer.flush()

                async with SessionFactory() as session:
                    repo = OutboxRepository(session)
                    for event, result in futures:
                        error_msg = None
                        if isinstance(result, KafkaError):
                            error_msg = str(result)
                        else:
                            try:
                                result.result()
                                await repo.mark_sent(event.id)
                                logger.info("Sent event %s to %s", event.id, event.topic)
                                continue
                            except KafkaError as exc:
                                error_msg = str(exc)
                                logger.error("Failed to send event %s: %s", event.id, exc)

                        is_final = await repo.record_failure(
                            event.id, settings.outbox_max_retries,
                        )
                        if is_final:
                            await _send_to_dlq(producer, event, error_msg)

                    await session.commit()

        except KafkaError as exc:
            logger.error("Outbox relay kafka error: %s", exc)

        await asyncio.sleep(settings.outbox_poll_interval)


async def _send_to_dlq(
    producer: KafkaProducer, event, error_msg: str | None,
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
    try:
        await producer.send(
            topic=settings.kafka_topic_dlq,
            key=str(event.aggregate_id),
            value=dlq_payload,
        )
        await producer.flush()
        logger.warning("Event %s sent to DLQ", event.id)
    except KafkaError as exc:
        logger.error("Failed to send event %s to DLQ: %s", event.id, exc)
