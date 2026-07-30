import asyncio
import logging

from aiokafka.errors import KafkaError

from src.config import settings
from src.database import SessionFactory
from src.kafka.producer import KafkaProducer
from src.repositories.outbox_repository import OutboxRepository

logger = logging.getLogger(__name__)


async def outbox_relay(producer: KafkaProducer) -> None:
    logger.info("Outbox relay started")

    while True:
        try:
            async with SessionFactory() as session:
                repo = OutboxRepository(session)
                events = await repo.claim_pending(settings.outbox_batch_size)
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
                        if isinstance(result, KafkaError):
                            await repo.record_failure(event.id, settings.outbox_max_retries)
                            continue
                        try:
                            result.result()
                            await repo.mark_sent(event.id)
                            logger.info("Sent outbox event %s to topic %s", event.id, event.topic)
                        except KafkaError as exc:
                            logger.error("Failed to send event %s: %s", event.id, exc)
                            await repo.record_failure(event.id, settings.outbox_max_retries)
                    await session.commit()

        except KafkaError as exc:
            logger.error("Outbox relay kafka error: %s", exc)

        await asyncio.sleep(settings.outbox_poll_interval)
