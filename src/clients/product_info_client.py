import logging
from http import HTTPStatus

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from src.config import Settings
from src.exceptions.not_found import NotFoundException
from src.exceptions.service_unavailable import ServiceUnavailableException
from src.schemas.product_info import ProductInfoBody, ProductInfoResponse

logger = logging.getLogger(__name__)

settings = Settings()

MAX_RETRIES = 3
BASE_DELAY = 0.5
MAX_DELAY = 10.0
REQUEST_TIMEOUT = 5.0

RETRYABLE_STATUSES = {
    HTTPStatus.REQUEST_TIMEOUT,
    HTTPStatus.TOO_MANY_REQUESTS,
}


class _RetryableStatus(Exception):
    pass


def _on_give_up(retry_state):
    raise ServiceUnavailableException("ProductInfoService")


_retry = retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=BASE_DELAY, max=MAX_DELAY),
    retry=retry_if_exception_type((_RetryableStatus, httpx.ConnectError, httpx.TimeoutException)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    retry_error_callback=_on_give_up,
)


class ProductInfoClient:
    def __init__(self) -> None:
        self.base_url = str(settings.product_info_service_url)

    async def get_product_info(self, product_id: str) -> ProductInfoResponse:
        response = await self._get(f"/api/v1/products/{product_id}/info")
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NotFoundException("ProductInfo", product_id)
        return ProductInfoResponse.model_validate(response.json())

    async def create_product_info(self, data: ProductInfoBody) -> ProductInfoResponse:
        response = await self._post("/api/v1/products/info", json=data.model_dump(mode="json"))
        return ProductInfoResponse.model_validate(response.json())

    @_retry
    async def _get(self, path: str) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(path)
        self._check_retryable(response)
        return response

    @_retry
    async def _post(self, path: str, json: dict) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(path, json=json)
        self._check_retryable(response)
        return response

    @staticmethod
    def _check_retryable(response: httpx.Response) -> None:
        if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR or response.status_code in RETRYABLE_STATUSES:
            logger.warning("Retryable status %s for %s %s", response.status_code, response.request.method, response.request.url)
            raise _RetryableStatus(str(response.status_code))
