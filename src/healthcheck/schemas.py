from enum import Enum

from pydantic import BaseModel


class HealthStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


class HealthCheckResponse(BaseModel):
    status: HealthStatus
