from fastapi import HTTPException
from uuid import UUID


class NotFoundException(HTTPException):
    def __init__(self, entity: str, entity_id: UUID | str):
        super().__init__(
            status_code=404,
            detail=f"{entity} with id={entity_id} not found",
        )


class AlreadyExistsException(HTTPException):
    def __init__(self, entity: str, detail: str = ""):
        super().__init__(
            status_code=409,
            detail=f"{entity} already exists. {detail}".strip(),
        )


class BadRequestException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)
