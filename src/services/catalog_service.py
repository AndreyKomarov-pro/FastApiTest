import logging
from uuid import UUID

from src.models import CategoryModel, ProductModel
from src.repositories.catalog_repository import CatalogRepository
from src.schemas.category import CategoryCreate, CategoryResponse
from src.schemas.pagination import PageResponse
from src.schemas.product import ProductCreateBody, ProductResponse

logger = logging.getLogger(__name__)


class CatalogService:
    def __init__(self, repo: CatalogRepository) -> None:
        self.repo = repo

    async def get_categories(self, page: int, size: int) -> PageResponse[CategoryResponse]:
        logger.debug("Listing categories page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.repo.get_all_categories(size, offset)
        return PageResponse.build(
            items=[CategoryResponse.model_validate(c) for c in items],
            page=page,
            size=size,
        )

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        logger.info("Creating category name=%s", data.body.name)
        category = CategoryModel(**data.body.model_dump())
        result = await self.repo.create_category(category)
        return CategoryResponse.model_validate(result)

    async def get_products(self, category_id: UUID, page: int, size: int) -> PageResponse[ProductResponse]:
        logger.debug("Listing products for category_id=%s page=%s size=%s", category_id, page, size)
        offset = (page - 1) * size
        items = await self.repo.get_products_by_category(category_id, size, offset)
        return PageResponse.build(
            items=[ProductResponse.model_validate(p) for p in items],
            page=page,
            size=size,
        )

    async def create_product(self, category_id: UUID, data: ProductCreateBody) -> ProductResponse:
        logger.info("Creating product in category_id=%s name=%s", category_id, data.body.name)
        product = ProductModel(**data.body.model_dump(), category_id=category_id)
        product = await self.repo.create_product(product)
        return ProductResponse.model_validate(product)
