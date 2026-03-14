from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    username: str


class UserUpdate(BaseModel):
    username: str | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}
