import asyncio
import logging

from aiokafka import AIOKafkaProducer

from src.config import settings

logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        async with self._lock:
            if self._producer is not None:
                return
            producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                enable_idempotence=True,
                acks="all",
                value_serializer=lambda v: v.encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await producer.start()
            self._producer = producer
            logger.info("Kafka producer started")

    async def stop(self) -> None:
        async with self._lock:
            if self._producer is None:
                return
            producer = self._producer
            self._producer = None
            await producer.stop()
            logger.info("Kafka producer stopped")

    async def send(self, topic: str, key: str, value: str) -> None:
        producer = self._producer
        if producer is None:
            raise RuntimeError("KafkaProducer is not started")
        await producer.send_and_wait(topic, value=value, key=key)
