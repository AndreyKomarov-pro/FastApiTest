from fastapi import APIRouter, status
from uuid import UUID

from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.router.category.service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate):
    async with CategoryService() as service:
        category = await service.create(data)
        return CategoryResponse.model_validate(category)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID):
    async with CategoryService() as service:
        category = await service.get(category_id)
        return CategoryResponse.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: UUID, data: CategoryUpdate):
    async with CategoryService() as service:
        category = await service.update(category_id, data)
        return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID):
    async with CategoryService() as service:
        await service.delete(category_id)
