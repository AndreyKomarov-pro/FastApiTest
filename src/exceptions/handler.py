from http import HTTPStatus

from fastapi import Request
from starlette.responses import JSONResponse

from src.exceptions.base import AppException
from src.exceptions.validation import ValidationException
from src.schemas.error import ValidationErrorResponse


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    body = ValidationErrorResponse(error=exc.message, field=exc.field)
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=body.model_dump(),
    )
