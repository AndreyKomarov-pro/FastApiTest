import logging
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException
from src.models import CategoryModel, ProductModel
from src.repositories.category_repository import CategoryRepository
from src.repositories.product_repository import ProductRepository
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.schemas.pagination import PageResponse
from src.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductCreateBody

logger = logging.getLogger(__name__)


class CatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.category_repo = CategoryRepository(session)
        self.product_repo = ProductRepository(session)

    async def _fetch_category(self, category_id: UUID) -> CategoryModel:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    async def _fetch_product(self, product_id: UUID) -> ProductModel:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        logger.info("Creating category name=%s", data.name)
        category = CategoryModel(**data.model_dump())
        result = await self.category_repo.create(category)
        logger.debug("Category created id=%s", result.id)
        return CategoryResponse.model_validate(result)

    async def get_category_by_id(self, category_id: UUID) -> CategoryResponse:
        logger.info("Fetching category id=%s", category_id)
        category = await self._fetch_category(category_id)
        logger.debug("Category fetched id=%s", category.id)
        return CategoryResponse.model_validate(category)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryResponse:
        logger.info("Updating category id=%s", category_id)
        category = await self._fetch_category(category_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(category, field, value)
        updated = await self.category_repo.update(category)
        logger.debug("Category updated id=%s", updated.id)
        return CategoryResponse.model_validate(updated)

    async def delete_category(self, category_id: UUID) -> None:
        logger.info("Deleting category id=%s", category_id)
        category = await self._fetch_category(category_id)
        await self.category_repo.delete(category)
        logger.debug("Category deleted id=%s", category_id)

    async def create_product(self, data: ProductCreate) -> ProductResponse:
        logger.info("Creating product name=%s category_id=%s", data.name, data.category_id)
        category = await self._fetch_category(data.category_id)
        product = ProductModel(**data.model_dump())
        product = await self.product_repo.create(product)
        product.category = category
        logger.debug("Product created id=%s", product.id)
        return ProductResponse.model_validate(product)

    async def get_product_by_id(self, product_id: UUID) -> ProductResponse:
        logger.debug("Fetching product id=%s", product_id)
        product = await self._fetch_product(product_id)
        return ProductResponse.model_validate(product)

    async def update_product(self, product_id: UUID, data: ProductUpdate) -> ProductResponse:
        logger.info("Updating product id=%s", product_id)
        product = await self._fetch_product(product_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(product, field, value)
        updated = await self.product_repo.update(product)
        logger.debug("Product updated id=%s", updated.id)
        return ProductResponse.model_validate(updated)

    async def get_categories(self, page: int, size: int) -> PageResponse[CategoryResponse]:
        logger.debug("Listing categories page=%s size=%s", page, size)
        offset = (page - 1) * size
        total = (await self.session.execute(select(func.count()).select_from(CategoryModel))).scalar_one()
        items = await self.category_repo.get_all(size, offset)
        return PageResponse.build(
            items=[CategoryResponse.model_validate(c) for c in items],
            total=total,
            page=page,
            size=size,
        )

    async def get_products(self, page: int, size: int) -> PageResponse[ProductResponse]:
        logger.debug("Listing products page=%s size=%s", page, size)
        offset = (page - 1) * size
        total = (await self.session.execute(select(func.count()).select_from(ProductModel))).scalar_one()
        items = await self.product_repo.get_all(size, offset)
        return PageResponse.build(
            items=[ProductResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            size=size,
        )

    async def delete_product(self, product_id: UUID) -> None:
        logger.info("Deleting product id=%s", product_id)
        product = await self._fetch_product(product_id)
        await self.product_repo.delete(product)
        logger.debug("Product deleted id=%s", product_id)

    async def get_products_by_category(self, category_id: UUID, page: int, size: int) -> PageResponse[ProductResponse]:
        logger.debug("Listing products for category_id=%s page=%s size=%s", category_id, page, size)
        await self._fetch_category(category_id)
        offset = (page - 1) * size
        total = (await self.session.execute(
            select(func.count()).select_from(ProductModel).where(ProductModel.category_id == category_id)
        )).scalar_one()
        items = await self.product_repo.get_by_category(category_id, size, offset)
        return PageResponse.build(
            items=[ProductResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            size=size,
        )

    async def create_product_in_category(self, category_id: UUID, data: ProductCreateBody) -> ProductResponse:
        logger.info("Creating product in category_id=%s name=%s", category_id, data.name)
        category = await self._fetch_category(category_id)
        product = ProductModel(**data.model_dump(), category_id=category_id)
        product = await self.product_repo.create(product)
        product.category = category
        logger.debug("Product created id=%s", product.id)
        return ProductResponse.model_validate(product)
