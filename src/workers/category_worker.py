import asyncio
import json
import logging
import random
from datetime import datetime, timedelta, timezone

import httpx

from src.clients.product_info_client import ProductInfoClient
from src.database import SessionFactory
from src.enums.category_status import CategoryStatus
from src.exceptions.not_found import NotFoundException
from src.exceptions.service_unavailable import ServiceUnavailableException
from src.models.category import CategoryModel
from src.repositories.category_repository import CategoryRepository
from src.schemas.product_info import ProductInfoBody

logger = logging.getLogger(__name__)

WORKER_INTERVAL = 10
BATCH_SIZE = 10
MAX_RETRIES = 5
BASE_BACKOFF = 2
MAX_BACKOFF = 300
SEMAPHORE_LIMIT = 5


def _calc_next_retry_at(retry_count: int) -> datetime:
    backoff = min(BASE_BACKOFF * (2 ** retry_count), MAX_BACKOFF)
    jitter = random.uniform(0, backoff * 0.1)
    return datetime.now(timezone.utc) + timedelta(seconds=backoff + jitter)


async def _fetch_from_external(
    client: ProductInfoClient,
    category: CategoryModel,
) -> None:
    payload = json.loads(category.payload_json)
    for item in payload:
        await client.create_product_info(ProductInfoBody.model_validate(item))


async def _update_status(
    category_id,
    status: CategoryStatus,
    last_error: str | None = None,
) -> None:
    async with SessionFactory() as session:
        repo = CategoryRepository(session)
        await repo.update_status(category_id, status, expected_status=CategoryStatus.PENDING, last_error=last_error)


async def _increment_retry(
    category_id,
    retry_count: int,
    last_error: str | None = None,
) -> None:
    async with SessionFactory() as session:
        repo = CategoryRepository(session)
        next_retry_at = _calc_next_retry_at(retry_count)
        await repo.increment_retry(category_id, next_retry_at, last_error=last_error)


RETRYABLE_EXCEPTIONS = (
    ServiceUnavailableException,
    httpx.ConnectError,
    httpx.TimeoutException,
    asyncio.TimeoutError,
    ConnectionError,
)


async def _process_category(
    client: ProductInfoClient,
    category: CategoryModel,
    semaphore: asyncio.Semaphore,
) -> None:
    async with semaphore:
        try:
            await _fetch_from_external(client, category)
            await _update_status(category.id, CategoryStatus.CONFIRMED)
            logger.info("Category %s confirmed", category.id)
            return
        except NotFoundException as exc:
            await _update_status(category.id, CategoryStatus.CANCELLED, last_error=str(exc))
            logger.warning("Category %s cancelled: %s", category.id, exc)
            return
        except RETRYABLE_EXCEPTIONS as exc:
            error_msg = str(exc)
        except Exception as exc:
            await _update_status(category.id, CategoryStatus.ERROR, last_error=str(exc))
            logger.error("Category %s marked ERROR: %s", category.id, exc)
            return

        if category.retry_count >= MAX_RETRIES:
            await _final_check(client, category, error_msg)
            return

        await _increment_retry(category.id, category.retry_count, last_error=error_msg)
        logger.warning("Category %s retry %d scheduled", category.id, category.retry_count + 1)


async def _final_check(
    client: ProductInfoClient,
    category: CategoryModel,
    last_error: str,
) -> None:
    try:
        await _fetch_from_external(client, category)
        await _update_status(category.id, CategoryStatus.CONFIRMED)
        logger.info("Category %s confirmed on final check", category.id)
    except NotFoundException:
        await _update_status(category.id, CategoryStatus.CANCELLED, last_error=last_error)
        logger.warning("Category %s cancelled after max retries", category.id)
    except Exception:
        await _update_status(category.id, CategoryStatus.FAILED, last_error=last_error)
        logger.error("Category %s failed after max retries", category.id)


async def category_worker() -> None:
    logger.info("Category worker started")
    client = ProductInfoClient()

    while True:
        try:
            async with SessionFactory() as session:
                repo = CategoryRepository(session)
                categories = await repo.claim_pending(BATCH_SIZE)

            if categories:
                semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
                tasks = [
                    _process_category(client, cat, semaphore)
                    for cat in categories
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for cat, result in zip(categories, results):
                    if isinstance(result, Exception):
                        logger.error("Task for category %s failed: %s", cat.id, result)

        except Exception as exc:
            logger.error("Category worker error: %s", exc)

        await asyncio.sleep(WORKER_INTERVAL)
