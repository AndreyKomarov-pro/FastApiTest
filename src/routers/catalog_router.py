from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.dependencies.catalog import get_catalog_service
from src.schemas.category import CategoryCreate, CategoryResponse
from src.schemas.pagination import PageResponse
from src.schemas.product import ProductCreateBody, ProductResponse
from src.services.catalog_service import CatalogService

router = APIRouter(tags=["Catalog"])


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


@router.get("/categories/{category_id}/products", response_model=PageResponse[ProductResponse])
async def list_products_by_category(
    category_id: UUID,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: CatalogService = Depends(get_catalog_service),
) -> PageResponse[ProductResponse]:
    return await service.get_products_by_category(category_id, page, size)


@router.post("/categories/{category_id}/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_in_category(
    category_id: UUID,
    data: ProductCreateBody,
    service: CatalogService = Depends(get_catalog_service),
) -> ProductResponse:
    return await service.create_product_in_category(category_id, data)
