import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException
from src.models import CategoryModel
from src.repositories.category_repository import CategoryRepository
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.category_repo = CategoryRepository(session)

    async def _fetch_category(self, category_id: UUID) -> CategoryModel:
        logger.debug("Fetching category id=%s", category_id)
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    async def get_categories(self, page: int, size: int) -> PageResponse[CategoryResponse]:
        logger.debug("Listing categories page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.category_repo.get_all(size, offset)
        return PageResponse.build(
            items=[CategoryResponse.model_validate(c) for c in items],
            page=page,
            size=size,
        )

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        logger.info("Creating category name=%s", data.name)
        category = CategoryModel(**data.model_dump())
        result = await self.category_repo.create(category)
        return CategoryResponse.model_validate(result)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryResponse:
        logger.info("Updating category id=%s", category_id)
        category = await self._fetch_category(category_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(category, field, value)
        updated = await self.category_repo.update(category)
        return CategoryResponse.model_validate(updated)

    async def delete_category(self, category_id: UUID) -> None:
        logger.info("Deleting category id=%s", category_id)
        category = await self._fetch_category(category_id)
        await self.category_repo.delete(category)
