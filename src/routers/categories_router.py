from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.dependencies.catalog import get_catalog_service
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.schemas.pagination import PageResponse
from src.services.catalog_service import CatalogService

router = APIRouter(tags=["Categories"])


@router.get("/categories/", response_model=PageResponse[CategoryResponse])
async def list_categories(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: CatalogService = Depends(get_catalog_service),
) -> PageResponse[CategoryResponse]:
    return await service.get_categories(page, size)


@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    service: CatalogService = Depends(get_catalog_service),
) -> CategoryResponse:
    return await service.create_category(data)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    service: CatalogService = Depends(get_catalog_service),
) -> CategoryResponse:
    return await service.get_category_by_id(category_id)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    service: CatalogService = Depends(get_catalog_service),
) -> CategoryResponse:
    return await service.update_category(category_id, data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    service: CatalogService = Depends(get_catalog_service),
) -> None:
    await service.delete_category(category_id)
