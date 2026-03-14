import uuid
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import Settings

logger = logging.getLogger(__name__)

settings = Settings()

engine: AsyncEngine = create_async_engine(
    str(settings.postgres_url),
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    request_id = str(uuid.uuid4())
    async with SessionFactory() as session:
        try:
            logger.info(f"[{request_id}] Session opened")
            yield session
            await session.commit()
            logger.info(f"[{request_id}] Session committed")
        except Exception as e:
            await session.rollback()
            logger.error(f"[{request_id}] Session rollback due to: {e}")
            raise
        finally:
            await session.close()
            logger.info(f"[{request_id}] Session closed")
