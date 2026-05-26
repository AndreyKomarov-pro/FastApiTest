from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.category import CategoryModel

class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.products))
            .where(CategoryModel.is_deleted == False)
            .order_by(CategoryModel.created_at.desc())
            .with_for_update(skip_locked=True)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, category_id: UUID) -> CategoryModel | None:
        result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.products))
            .where(CategoryModel.id == category_id, CategoryModel.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def create(self, category: CategoryModel) -> CategoryModel:
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category, attribute_names=["products"])
        return category

    async def update(self, category: CategoryModel) -> CategoryModel:
        await self.session.flush()
        await self.session.refresh(category, attribute_names=["products"])
        return category

    async def delete(self, category: CategoryModel) -> None:
        category.is_deleted = True
        await self.session.flush()
