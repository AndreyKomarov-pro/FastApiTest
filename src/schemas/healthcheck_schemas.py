from http import HTTPStatus

from pydantic import BaseModel

HEALTH_STATUS_OK = HTTPStatus.OK.phrase


class HealthCheckResponse(BaseModel):
    status: str
