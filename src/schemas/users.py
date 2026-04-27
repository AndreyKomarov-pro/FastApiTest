from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserBody(BaseModel):
    username: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Имя пользователя не может быть пустым")
        return stripped


class UserCreate(BaseModel):
    body: UserBody


class UserUpdate(BaseModel):
    body: UserBody


class UserResponse(BaseModel):
    id: UUID
    body: UserBody
    created_at: datetime

    model_config = {"from_attributes": True}
