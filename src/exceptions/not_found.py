from http import HTTPStatus
from uuid import UUID

from src.exceptions.base import AppException


class NotFoundException(AppException):
    status_code = HTTPStatus.NOT_FOUND

    def __init__(self, entity: str, entity_id: UUID | str):
        super().__init__(f"{entity} with id={entity_id} not found")
