from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.schemas.pagination import PageResponse
from src.schemas.product import ProductCreateBody, ProductUpdate, ProductResponse
from src.services.category_service import CategoryService
from src.services.product_service import ProductService

router = APIRouter(tags=["Catalog"])


@router.get("/categories/", response_model=PageResponse[CategoryResponse])
async def list_categories(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PageResponse[CategoryResponse]:
    service = CategoryService(session)
    return await service.get_categories(page, size)


@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    service = CategoryService(session)
    return await service.create_category(data)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    session: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    service = CategoryService(session)
    return await service.update_category(category_id, data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    service = CategoryService(session)
    await service.delete_category(category_id)


@router.get("/categories/{category_id}/products", response_model=PageResponse[ProductResponse])
async def list_products(
    category_id: UUID,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PageResponse[ProductResponse]:
    service = ProductService(session)
    return await service.get_products(category_id, page, size)


@router.post("/categories/{category_id}/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    category_id: UUID,
    data: ProductCreateBody,
    session: AsyncSession = Depends(get_db),
) -> ProductResponse:
    service = ProductService(session)
    return await service.create_product(category_id, data)


@router.put("/categories/{category_id}/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
    session: AsyncSession = Depends(get_db),
) -> ProductResponse:
    service = ProductService(session)
    return await service.update_product(product_id, data)


@router.delete("/categories/{category_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    service = ProductService(session)
    await service.delete_product(product_id)
