from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.catalog_repository import CatalogRepository
from src.schemas.category import CategoryCreate, CategoryResponse
from src.schemas.pagination import PageResponse
from src.schemas.product import ProductCreateBody, ProductResponse
from src.services.catalog_service import CatalogService

router = APIRouter(tags=["Catalog"])


@router.get("/categories/", response_model=PageResponse[CategoryResponse])
async def list_categories(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PageResponse[CategoryResponse]:
    service = CatalogService(CatalogRepository(session))
    return await service.get_categories(page, size)


@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    service = CatalogService(CatalogRepository(session))
    return await service.create_category(data)


@router.get("/categories/{category_id}/products", response_model=PageResponse[ProductResponse])
async def list_products(
    category_id: UUID,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PageResponse[ProductResponse]:
    service = CatalogService(CatalogRepository(session))
    return await service.get_products(category_id, page, size)


@router.post("/categories/{category_id}/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    category_id: UUID,
    data: ProductCreateBody,
    session: AsyncSession = Depends(get_db),
) -> ProductResponse:
    service = CatalogService(CatalogRepository(session))
    return await service.create_product(category_id, data)
