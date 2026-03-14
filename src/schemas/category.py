from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
