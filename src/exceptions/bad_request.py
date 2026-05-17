from http import HTTPStatus

from src.exceptions.base import AppException


class BadRequestException(AppException):
    status_code = HTTPStatus.BAD_REQUEST
