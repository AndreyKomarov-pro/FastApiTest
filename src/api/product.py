from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from src.models import ProductModel, CategoryModel
from src.database import get_session
from src.schemas.product import ProductCreate, ProductResponse


router = APIRouter(prefix="/products", tags=["Products"])


async def get_product_with_relations(product_id: UUID, session: AsyncSession) -> ProductModel:
    result = await session.execute(
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .options(selectinload(ProductModel.category))
    )
    return result.scalar_one_or_none()


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_session),
):
    category = await session.get(CategoryModel, product_data.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    product = ProductModel(**product_data.model_dump())
    session.add(product)
    await session.flush()
    await session.commit()

    product = await get_product_with_relations(product.id, session)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    product = await get_product_with_relations(product_id, session)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(ProductModel, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_data.category_id != product.category_id:
        category = await session.get(CategoryModel, product_data.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")

    for key, value in product_data.model_dump().items():
        setattr(product, key, value)

    await session.commit()

    product = await get_product_with_relations(product_id, session)
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(ProductModel, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await session.delete(product)
    await session.commit()
    return {"message": "Product deleted successfully"}