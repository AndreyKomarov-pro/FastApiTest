from fastapi import HTTPException


class AlreadyExistsException(HTTPException):
    def __init__(self, entity: str, detail: str = ""):
        super().__init__(
            status_code=409,
            detail=f"{entity} already exists. {detail}".strip(),
        )
