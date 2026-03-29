from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.catalog_schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse,
)
from src.services.catalog_service import CatalogService

router = APIRouter(tags=["Catalog"])


def get_service(session: AsyncSession = Depends(get_db)) -> CatalogService:
    return CatalogService(session)


@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    service: CatalogService = Depends(get_service),
) -> CategoryResponse:
    category = await service.create_category(data)
    return CategoryResponse.model_validate(category)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    service: CatalogService = Depends(get_service),
) -> CategoryResponse:
    category = await service.get_category_by_id(category_id)
    return CategoryResponse.model_validate(category)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    service: CatalogService = Depends(get_service),
) -> CategoryResponse:
    category = await service.update_category(category_id, data)
    return CategoryResponse.model_validate(category)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    service: CatalogService = Depends(get_service),
) -> None:
    await service.delete_category(category_id)


@router.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    service: CatalogService = Depends(get_service),
) -> ProductResponse:
    product = await service.create_product(data)
    return ProductResponse.model_validate(product)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    service: CatalogService = Depends(get_service),
) -> ProductResponse:
    product = await service.get_product_by_id(product_id)
    return ProductResponse.model_validate(product)


@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    service: CatalogService = Depends(get_service),
) -> ProductResponse:
    product = await service.update_product(product_id, data)
    return ProductResponse.model_validate(product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    service: CatalogService = Depends(get_service),
) -> None:
    await service.delete_product(product_id)
