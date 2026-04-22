from fastapi import HTTPException
from starlette import status


class AlreadyExistsException(HTTPException):
    def __init__(self, entity: str, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity} already exists. {detail}",
        )
