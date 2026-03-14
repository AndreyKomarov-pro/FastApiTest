from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import CategoryModel
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.exceptions import NotFoundException
from src.router.category.repository import CategoryRepository


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.repo = CategoryRepository(session)

    async def create(self, data: CategoryCreate) -> CategoryModel:
        return await self.repo.create(
            name=data.name,
            description=data.description,
        )

    async def get(self, category_id: UUID) -> CategoryModel:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    async def update(self, category_id: UUID, data: CategoryUpdate) -> CategoryModel:
        category = await self.get(category_id)
        return await self.repo.update(
            category=category,
            name=data.name,
            description=data.description,
        )

    async def delete(self, category_id: UUID) -> None:
        category = await self.get(category_id)
        await self.repo.delete(category)
