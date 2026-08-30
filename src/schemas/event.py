from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from src.models.enums.event_type import EventType


class EventEnvelope(BaseModel):
    event_id: UUID
    event_type: EventType
    aggregate_type: str
    aggregate_id: UUID
    timestamp: datetime
    data: dict[str, Any]
