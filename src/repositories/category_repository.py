from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CategoryModel


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, category_id: UUID) -> CategoryModel | None:
        return await self.session.get(CategoryModel, category_id)

    async def get_all(self, limit: int, offset: int) -> list[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel).order_by(CategoryModel.created_at.desc()).limit(limit).offset(offset).with_for_update(skip_locked=True)
        )
        return list(result.scalars().all())

    async def create(self, category: CategoryModel) -> CategoryModel:
        self.session.add(category)
        await self.session.flush()
        return category

    async def update(self, category: CategoryModel) -> CategoryModel:
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category: CategoryModel) -> None:
        await self.session.delete(category)
