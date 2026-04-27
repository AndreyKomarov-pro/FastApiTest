from starlette import status

from src.exceptions.base import AppException


class BadRequestException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
