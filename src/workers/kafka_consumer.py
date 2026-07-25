import json
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from src.clients.kafka_producer import KafkaProducer
from src.config import settings
from src.database import SessionFactory
from src.models.processed_event import ProcessedEventModel
from src.repositories.processed_event_repository import ProcessedEventRepository

logger = logging.getLogger(__name__)


async def consume_events(producer: KafkaProducer) -> None:
    consumer = AIOKafkaConsumer(
        *settings.kafka_topics,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: v.decode("utf-8"),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
    )
    await consumer.start()
    logger.info("Kafka consumer started")

    try:
        async for msg in consumer:
            try:
                envelope = json.loads(msg.value)
                event_id = UUID(envelope["event_id"])

                async with SessionFactory() as session:
                    repo = ProcessedEventRepository(session)

                    saved = await repo.save_if_not_exists(
                        ProcessedEventModel(
                            event_id=event_id,
                            topic=msg.topic,
                            event_type=envelope["event_type"],
                        )
                    )

                    if not saved:
                        logger.debug("Duplicate event %s, skipping", event_id)
                        await consumer.commit()
                        continue

                    await session.commit()

                logger.info(
                    "Processed event %s type=%s from %s",
                    event_id, envelope["event_type"], msg.topic,
                )
                await consumer.commit()

            except KafkaError:
                raise
            except Exception as exc:
                logger.error("Failed to process message: %s", exc)
                dlq_sent = await _send_to_dlq(producer, msg)
                if dlq_sent:
                    await consumer.commit()
    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")


async def _send_to_dlq(producer: KafkaProducer, msg) -> bool:
    dlq_payload = json.dumps({
        "original_topic": msg.topic,
        "key": msg.key,
        "value": msg.value if isinstance(msg.value, str) else msg.value.decode("utf-8"),
        "partition": msg.partition,
        "offset": msg.offset,
    })
    try:
        await producer.send(
            topic=settings.kafka_topic_dlq,
            key=msg.key or "",
            value=dlq_payload,
        )
        await producer.flush()
        logger.warning("Message sent to DLQ from topic=%s offset=%s", msg.topic, msg.offset)
        return True
    except KafkaError as exc:
        logger.error("Failed to send to DLQ: %s", exc)
        return False
