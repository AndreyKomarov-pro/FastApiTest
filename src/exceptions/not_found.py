from uuid import UUID
from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, entity: str, entity_id: UUID | str):
        super().__init__(
            status_code=404,
            detail=f"{entity} with id={entity_id} not found",
        )
