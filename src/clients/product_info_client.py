import logging
from http import HTTPStatus

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from src.config import Settings
from src.enums.retryable_status import RetryableStatus
from src.exceptions.not_found import NotFoundException
from src.exceptions.retryable_status import RetryableStatusException
from src.exceptions.service_unavailable import ServiceUnavailableException
from src.schemas.product_info import ProductInfoBody, ProductInfoResponse

logger = logging.getLogger(__name__)

settings = Settings()


def _on_give_up(retry_state):
    raise ServiceUnavailableException("ProductInfoService")


_retry = retry(
    stop=stop_after_attempt(settings.client_max_retries),
    wait=wait_exponential(multiplier=settings.client_base_delay, max=settings.client_max_delay),
    retry=retry_if_exception_type((RetryableStatusException, httpx.ConnectError, httpx.TimeoutException)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    retry_error_callback=_on_give_up,
)


class ProductInfoClient:
    def __init__(self) -> None:
        self.base_url = str(settings.product_info_service_url)

    async def get_product_info(self, product_id: str) -> ProductInfoResponse:
        logger.info("Fetching product info for product_id=%s", product_id)
        response = await self._get(f"/api/v1/products/{product_id}/info")
        if response.status_code == HTTPStatus.NOT_FOUND:
            logger.warning("Product info not found for product_id=%s", product_id)
            raise NotFoundException("ProductInfo", product_id)
        logger.info("Product info fetched for product_id=%s", product_id)
        return ProductInfoResponse.model_validate(response.json())

    async def create_product_info(self, data: ProductInfoBody) -> ProductInfoResponse:
        logger.info("Creating product info for product_id=%s", data.product_id)
        response = await self._post("/api/v1/products/info", json=data.model_dump(mode="json"))
        logger.info("Product info created for product_id=%s", data.product_id)
        return ProductInfoResponse.model_validate(response.json())

    @_retry
    async def _get(self, path: str) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=settings.client_request_timeout) as client:
            response = await client.get(path)
        self._check_retryable(response)
        return response

    @_retry
    async def _post(self, path: str, json: dict) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=settings.client_request_timeout) as client:
            response = await client.post(path, json=json)
        self._check_retryable(response)
        return response

    @staticmethod
    def _check_retryable(response: httpx.Response) -> None:
        if response.status_code in RetryableStatus:
            logger.warning("Retryable status %s for %s %s", response.status_code, response.request.method, response.request.url)
            raise RetryableStatusException(str(response.status_code))
