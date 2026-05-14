import logging
from uuid import UUID
from src.exceptions import NotFoundException
from src.repositories.catalog_repository import CatalogRepository
from src.schemas.catalog import CategoryCreate, CategoryUpdate, CategoryResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)

class CatalogService:
    def __init__(self, repo: CatalogRepository) -> None:
        self.repo = repo

    async def get_categories(self, page: int, size: int) -> PageResponse[CategoryResponse]:
        logger.debug("Listing categories page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        return PageResponse(
            items=CategoryResponse.from_list(items),
            page=page,
            size=size,
        )

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        logger.info("Creating category name=%s", data.body.name)
        category = data.body.to_model()
        result = await self.repo.create(category)
        return CategoryResponse.from_model(result)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryResponse:
        logger.info("Updating category id=%s", category_id)
        category = await self.repo.get_by_id_for_update(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        self._update_fields(category, {"name": data.body.name, "description": data.body.description})
        result = await self.repo.update(category)
        return CategoryResponse.from_model(result)

    async def delete_category(self, category_id: UUID) -> None:
        logger.info("Deleting category id=%s", category_id)
        category = await self.repo.get_by_id_for_update(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        await self.repo.delete(category)

    @staticmethod
    def _update_fields(obj, fields: dict) -> None:
        for field, value in fields.items():
            setattr(obj, field, value)
