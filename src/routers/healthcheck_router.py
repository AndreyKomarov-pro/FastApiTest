from fastapi import APIRouter

from src.schemas.healthcheck_schemas import HealthCheckResponse, HEALTH_STATUS_OK

router = APIRouter(tags=["Health"])


@router.get("/healthcheck", response_model=HealthCheckResponse)
async def healthcheck() -> HealthCheckResponse:
    return HealthCheckResponse(status=HEALTH_STATUS_OK)
