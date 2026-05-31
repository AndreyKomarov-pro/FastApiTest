import os
import subprocess
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import redis.asyncio as redis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from src.application import get_app
from src.cache.redis_client import RedisClient, get_redis
from src.clients.product_info_client import ProductInfoClient
from src.database import get_db
from src.dependencies import get_product_info_client


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:14", driver="asyncpg") as pg:
        yield pg


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as r:
        yield r


@pytest.fixture(scope="session")
def db_url(postgres_container) -> str:
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session", autouse=True)
def run_migrations(db_url):
    env = os.environ.copy()
    env["POSTGRES_URL"] = db_url
    subprocess.run(
        ["alembic", "upgrade", "head"],
        env=env,
        check=True,
    )


@pytest.fixture
async def session(db_url) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(db_url, poolclass=NullPool)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
        await s.rollback()
    await engine.dispose()


@pytest.fixture
async def redis_client(redis_container) -> AsyncGenerator[redis.Redis, None]:
    url = f"redis://{redis_container.get_container_host_ip()}:{redis_container.get_exposed_port(6379)}"
    r = redis.from_url(url, decode_responses=True)
    yield r
    await r.flushdb()
    await r.aclose()


@pytest.fixture
def cache_service(redis_client) -> RedisClient:
    return RedisClient(redis_client)


@pytest.fixture
def mock_product_info_client() -> AsyncMock:
    return AsyncMock(spec=ProductInfoClient)


@pytest.fixture
async def client(session, redis_client, mock_product_info_client) -> AsyncGenerator[AsyncClient, None]:
    app = get_app()

    async def override_get_db():
        yield session

    async def override_get_redis():
        return redis_client

    def override_get_product_info_client():
        return mock_product_info_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_product_info_client] = override_get_product_info_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
