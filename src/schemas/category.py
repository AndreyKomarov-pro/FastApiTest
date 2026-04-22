from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    description: Optional[str] = Field(default=None, max_length=1000, description="Описание категории")

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Название категории не может быть пустым")
        return stripped


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Название категории")
    description: Optional[str] = Field(default=None, max_length=1000, description="Описание категории")

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Название категории не может быть пустым")
            return stripped
        return v

    @field_validator("name", mode="before")
    @classmethod
    def not_null(cls, v: object) -> object:
        if v is None:
            raise ValueError("Поле не может быть null")
        return v


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
