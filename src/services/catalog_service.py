import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException
from src.models import CategoryModel, ProductModel
from src.repositories.category_repository import CategoryRepository
from src.repositories.product_repository import ProductRepository
from src.schemas.catalog_schemas import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


class CatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self.category_repo = CategoryRepository(session)
        self.product_repo = ProductRepository(session)

    @staticmethod
    def _to_category_model(data: CategoryCreate) -> CategoryModel:
        return CategoryModel(name=data.name, description=data.description)

    @staticmethod
    def _to_product_model(data: ProductCreate) -> ProductModel:
        return ProductModel(
            name=data.name,
            description=data.description,
            price=data.price,
            quantity=data.quantity,
            category_id=data.category_id,
        )

    async def create_category(self, data: CategoryCreate) -> CategoryModel:
        logger.info("Creating category name=%s", data.name)
        category = self._to_category_model(data)
        return await self.category_repo.create(category)

    async def get_category_by_id(self, category_id: UUID) -> CategoryModel:
        logger.debug("Fetching category id=%s", category_id)
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryModel:
        logger.info("Updating category id=%s", category_id)
        category = await self.get_category_by_id(category_id)
        if data.name is not None:
            category.name = data.name
        if data.description is not None:
            category.description = data.description
        return await self.category_repo.update(category)

    async def delete_category(self, category_id: UUID) -> None:
        logger.info("Deleting category id=%s", category_id)
        category = await self.get_category_by_id(category_id)
        await self.category_repo.delete(category)

    async def create_product(self, data: ProductCreate) -> ProductModel:
        logger.info("Creating product name=%s category_id=%s", data.name, data.category_id)
        category = await self.get_category_by_id(data.category_id)
        product = self._to_product_model(data)
        product = await self.product_repo.create(product)
        product.category = category
        return product

    async def get_product_by_id(self, product_id: UUID) -> ProductModel:
        logger.debug("Fetching product id=%s", product_id)
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product

    async def update_product(self, product_id: UUID, data: ProductUpdate) -> ProductModel:
        logger.info("Updating product id=%s", product_id)
        product = await self.get_product_by_id(product_id)
        if data.category_id is not None:
            await self.get_category_by_id(data.category_id)
        if data.name is not None:
            product.name = data.name
        if data.description is not None:
            product.description = data.description
        if data.price is not None:
            product.price = data.price
        if data.quantity is not None:
            product.quantity = data.quantity
        if data.category_id is not None:
            product.category_id = data.category_id
        return await self.product_repo.update(product)

    async def delete_product(self, product_id: UUID) -> None:
        logger.info("Deleting product id=%s", product_id)
        product = await self.get_product_by_id(product_id)
        await self.product_repo.delete(product)
