from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.outbox_event import OutboxEventModel


class OutboxEventToSend(BaseModel):
    id: UUID
    aggregate_id: UUID
    topic: str
    payload: str
    attempts: int
    processing_id: UUID

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model: OutboxEventModel) -> "OutboxEventToSend":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models: list[OutboxEventModel]) -> list["OutboxEventToSend"]:
        return [cls.model_validate(model) for model in models]
