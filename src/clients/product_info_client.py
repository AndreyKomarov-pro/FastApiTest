import asyncio
import logging
import random
from http import HTTPStatus

import httpx

from src.clients.circuit_breaker import CircuitBreaker
from src.config import Settings
from src.exceptions.service_unavailable import ServiceUnavailableException
from src.schemas.product_info import ProductInfoBody, ProductInfoResponse

logger = logging.getLogger(__name__)

settings = Settings()

MAX_RETRIES = 3
BASE_DELAY = 0.5
MAX_DELAY = 10.0
JITTER_MAX = 0.5
REQUEST_TIMEOUT = 5.0


class ProductInfoClient:
    _circuit_breaker = CircuitBreaker()

    def __init__(self) -> None:
        self.base_url = str(settings.product_info_service_url)

    async def get_product_info(self, product_id: str) -> ProductInfoResponse | None:
        return await self._request(
            "GET",
            f"/api/v1/products/{product_id}/info",
            response_model=ProductInfoResponse,
        )

    async def create_product_info(self, data: ProductInfoBody) -> ProductInfoResponse:
        return await self._request(
            "POST",
            "/api/v1/products/info",
            json=data.model_dump(mode="json"),
            response_model=ProductInfoResponse,
        )

    async def _request(
        self,
        method: str,
        path: str,
        response_model: type[ProductInfoResponse] = ProductInfoResponse,
        json: dict | None = None,
    ) -> ProductInfoResponse | None:
        if not self._circuit_breaker.allow_request():
            raise ServiceUnavailableException("ProductInfoService")

        last_exc = None
        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=REQUEST_TIMEOUT,
                ) as client:
                    response = await client.request(method, path, json=json)

                if response.status_code == HTTPStatus.NOT_FOUND:
                    self._circuit_breaker.record_success()
                    return None

                if response.status_code in (
                    HTTPStatus.OK,
                    HTTPStatus.CREATED,
                ):
                    self._circuit_breaker.record_success()
                    return response_model.model_validate(response.json())

                if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                    last_exc = httpx.HTTPStatusError(
                        f"Server error {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                    self._circuit_breaker.record_failure()
                    await self._backoff(attempt)
                    continue

                self._circuit_breaker.record_success()
                return None

            except httpx.TransportError as exc:
                last_exc = exc
                self._circuit_breaker.record_failure()
                logger.warning(
                    "Request failed attempt=%d error=%s", attempt + 1, exc
                )
                await self._backoff(attempt)

        logger.error("All retries exhausted for %s %s", method, path)
        raise ServiceUnavailableException("ProductInfoService")

    @staticmethod
    async def _backoff(attempt: int) -> None:
        delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
        jitter = random.uniform(0, JITTER_MAX)
        await asyncio.sleep(delay + jitter)
