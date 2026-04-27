from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CategoryBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    description: Optional[str] = Field(default=None, max_length=1000, description="Описание категории")

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Название категории не может быть пустым")
        return stripped

    @field_validator("description")
    @classmethod
    def strip_description(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = v.strip()
        return stripped or None


class CategoryCreate(BaseModel):
    body: CategoryBody


class CategoryResponse(BaseModel):
    id: UUID
    body: CategoryBody
    created_at: datetime

    model_config = {"from_attributes": True}
