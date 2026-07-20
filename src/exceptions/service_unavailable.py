from http import HTTPStatus

from src.exceptions.base import AppException


class ServiceUnavailableException(AppException):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE

    def __init__(self, service: str):
        super().__init__(f"{service} is temporarily unavailable")
