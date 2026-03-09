from fastapi import APIRouter, Depends, HTTPException
from src.models import CategoryModel
from src.database import get_session
from src.schemas.category import CategoryCreate, CategoryResponse
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/category", tags=["Category"])


@router.post("/", response_model=CategoryResponse)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
):
    category = CategoryModel(**data.model_dump())
    session.add(category)
    await session.flush()  # получаем id
    await session.refresh(category)  # читаем из БД
    await session.commit()  # фиксируем транзакцию
    return category


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID,session: AsyncSession = Depends(get_session),):
    category = await session.get(CategoryModel, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
):
        category = await session.get(CategoryModel, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        for key, value in category_data.model_dump().items():
            setattr(category, key, value)

        await session.commit()
        await session.refresh(category)
        return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    session: AsyncSession = Depends(get_session),
):
        category = await session.get(CategoryModel, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        await session.delete(category)
        await session.commit()
        return {"message": "Category deleted successfully"}