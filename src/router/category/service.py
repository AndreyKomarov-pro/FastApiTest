from uuid import UUID
from src.models import CategoryModel
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.exceptions import NotFoundException
from src.router.category.repository import CategoryRepository
from src.database import get_session


class CategoryService:
    def __init__(self):
        self._session = None
        self.repo = None

    async def __aenter__(self):
        self._ctx = get_session()
        self._session = await self._ctx.__aenter__()
        self.repo = CategoryRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._ctx.__aexit__(exc_type, exc_val, exc_tb)

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
