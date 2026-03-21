from fastapi import APIRouter

from src.healthcheck.schemas import HealthCheckResponse, HealthStatus

router = APIRouter(tags=["Health"])


@router.get("/healthcheck", response_model=HealthCheckResponse)
async def healthcheck() -> HealthCheckResponse:
    return HealthCheckResponse(status=HealthStatus.OK)
