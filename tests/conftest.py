import os
import subprocess
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import fakeredis.aioredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from src.application import get_app
from src.cache.cache_service import CacheService
from src.cache.redis import get_redis
from src.clients.product_info_client import ProductInfoClient
from src.database import get_db
from src.dependencies import get_product_info_client


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:14", driver="asyncpg") as pg:
        yield pg


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
async def fake_redis():
    r = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield r
    await r.flushall()
    await r.aclose()


@pytest.fixture
def cache_service(fake_redis) -> CacheService:
    return CacheService(fake_redis)


@pytest.fixture
def mock_product_info_client() -> AsyncMock:
    return AsyncMock(spec=ProductInfoClient)


@pytest.fixture
async def client(session, fake_redis, mock_product_info_client) -> AsyncGenerator[AsyncClient, None]:
    app = get_app()

    async def override_get_db():
        yield session

    async def override_get_redis():
        return fake_redis

    def override_get_product_info_client():
        return mock_product_info_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_product_info_client] = override_get_product_info_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
