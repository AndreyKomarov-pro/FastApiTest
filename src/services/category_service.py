import logging
from uuid import UUID
from src.exceptions import NotFoundException
from src.models.category import CategoryModel
from src.models.product import ProductModel
from src.repositories.category_repository import CategoryRepository
from src.schemas.catalog import CategoryCreate, CategoryUpdate, CategoryUpdateBody, CategoryResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, repo: CategoryRepository) -> None:
        self.repo = repo

    async def _get_category_orm(self, category_id: UUID) -> CategoryModel:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    async def get_categories(self, page: int, size: int) -> PageResponse[CategoryResponse]:
        logger.debug("Listing categories page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        return PageResponse(
            items=CategoryResponse.from_list(items),
            page=page,
            size=size,
        )

    async def get_category_by_id(self, category_id: UUID) -> CategoryResponse:
        logger.debug("Fetching category id=%s", category_id)
        category = await self._get_category_orm(category_id)
        return CategoryResponse.from_model(category)

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        logger.info("Creating category name=%s", data.body.name)
        category = CategoryModel(name=data.body.name, description=data.body.description)
        category.products = [
            ProductModel(
                name=p.name,
                description=p.description,
                price=p.price,
                quantity=p.quantity,
            )
            for p in data.body.products
        ]
        result = await self.repo.create(category)
        return CategoryResponse.from_model(result)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryResponse:
        logger.info("Updating category id=%s", category_id)
        category = await self._get_category_orm(category_id)
        self._update_fields(category, data.body)
        result = await self.repo.update(category)
        return CategoryResponse.from_model(result)

    async def delete_category(self, category_id: UUID) -> None:
        logger.info("Deleting category id=%s", category_id)
        category = await self._get_category_orm(category_id)
        await self.repo.delete(category)

    @staticmethod
    def _update_fields(category: CategoryModel, fields: CategoryUpdateBody) -> None:
        for key, value in fields.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
