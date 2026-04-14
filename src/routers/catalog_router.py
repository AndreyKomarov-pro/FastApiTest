from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.dependencies.catalog import get_catalog_service
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.schemas.pagination import PageResponse
from src.schemas.product import ProductCreate, ProductUpdate, ProductResponse
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


@router.get("/products/", response_model=PageResponse[ProductResponse])
async def list_products(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: CatalogService = Depends(get_catalog_service),
) -> PageResponse[ProductResponse]:
    return await service.get_products(page, size)


@router.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    service: CatalogService = Depends(get_catalog_service),
) -> ProductResponse:
    return await service.create_product(data)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    service: CatalogService = Depends(get_catalog_service),
) -> ProductResponse:
    return await service.get_product_by_id(product_id)


@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    service: CatalogService = Depends(get_catalog_service),
) -> ProductResponse:
    return await service.update_product(product_id, data)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    service: CatalogService = Depends(get_catalog_service),
) -> None:
    await service.delete_product(product_id)
