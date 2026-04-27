from starlette import status

from src.exceptions.base import AppException


class AlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, entity: str, detail: str):
        super().__init__(f"{entity} already exists. {detail}")
