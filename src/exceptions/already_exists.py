from http import HTTPStatus

from src.exceptions.base import AppException


class AlreadyExistsException(AppException):
    status_code = HTTPStatus.CONFLICT

    def __init__(self, entity: str, detail: str):
        super().__init__(f"{entity} already exists. {detail}")
