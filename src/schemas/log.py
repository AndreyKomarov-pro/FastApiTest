from typing import TypedDict


class RequestLogExtra(TypedDict):
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
