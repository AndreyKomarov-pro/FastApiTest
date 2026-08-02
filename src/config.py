import os

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn
    redis_url: str = "redis://localhost:6379/0"
    product_info_service_url: str = "http://localhost:8001"

    client_max_retries: int = 3
    client_base_delay: float = 0.5
    client_max_delay: float = 10.0
    client_request_timeout: float = 5.0

    worker_interval: int = 10
    worker_batch_size: int = 10
    worker_max_retries: int = 5
    worker_base_backoff: int = 2
    worker_max_backoff: int = 300
    worker_semaphore_limit: int = 5

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_users: str = "users"
    kafka_topic_dlq: str = "dlq"

    outbox_poll_interval: int = 5
    outbox_batch_size: int = 50
    outbox_max_retries: int = 5
    outbox_processing_timeout: int = 300

    class Config:
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.env'
        )


settings = Settings()
