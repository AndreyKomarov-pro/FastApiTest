from uuid import UUID

from fastapi import HTTPException
from starlette import status


class NotFoundException(HTTPException):
    def __init__(self, entity: str, entity_id: UUID | str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} with id={entity_id} not found",
        )
