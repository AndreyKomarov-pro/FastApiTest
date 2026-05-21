from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from src.dependencies import get_category_service
from src.schemas.catalog import CategoryCreate, CategoryUpdate, CategoryResponse
from src.schemas.pagination import PageResponse
from src.services.category_service import CategoryService

router = APIRouter(tags=["Catalog"])

@router.get("/categories/", response_model=PageResponse[CategoryResponse])
async def list_categories(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: CategoryService = Depends(get_category_service),
) -> PageResponse[CategoryResponse]:
    return await service.get_categories(page, size)

@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    return await service.get_category_by_id(category_id)

@router.post("/categories/", response_model=CategoryResponse, status_code=HTTPStatus.CREATED)
async def create_category(
    data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    return await service.create_category(data)

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    return await service.update_category(category_id, data)

@router.delete("/categories/{category_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
) -> None:
    await service.delete_category(category_id)
