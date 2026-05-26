from pydantic import BaseModel

class ValidationErrorResponse(BaseModel):
    error: str
    field: str
