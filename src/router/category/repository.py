from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import CategoryModel


class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, category_id: UUID) -> CategoryModel | None:
        return await self.session.get(CategoryModel, category_id)

    async def create(self, name: str, description: str | None) -> CategoryModel:
        category = CategoryModel(name=name, description=description)
        self.session.add(category)
        await self.session.flush()
        return category

    async def update(self, category: CategoryModel, name: str | None, description: str | None) -> CategoryModel:
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        await self.session.flush()
        return category

    async def delete(self, category: CategoryModel) -> None:
        await self.session.delete(category)
