import os

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn
    redis_url: str = "redis://localhost:6379/0"
    product_info_service_url: str = "http://localhost:8001"

    class Config:
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.env'
        )