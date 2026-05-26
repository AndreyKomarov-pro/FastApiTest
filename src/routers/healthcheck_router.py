from http import HTTPStatus

from fastapi import APIRouter

from src.schemas.healthcheck import HealthCheckResponse

router = APIRouter(tags=["Health"])


@router.get("/healthcheck", response_model=HealthCheckResponse)
async def healthcheck() -> HealthCheckResponse:
    return HealthCheckResponse(status=HTTPStatus.OK.name.lower())
