from fastapi import APIRouter, status
from uuid import UUID

from src.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from src.router.product.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate):
    async with ProductService() as service:
        product = await service.create(data)
        return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID):
    async with ProductService() as service:
        product = await service.get(product_id)
        return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, data: ProductUpdate):
    async with ProductService() as service:
        product = await service.update(product_id, data)
        return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID):
    async with ProductService() as service:
        await service.delete(product_id)
