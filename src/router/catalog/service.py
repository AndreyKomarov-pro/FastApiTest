from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException
from src.models import CategoryModel, ProductModel
from src.router.catalog.repository import CategoryRepository, ProductRepository
from src.router.catalog.schemas import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate


class CatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self.category_repo = CategoryRepository(session)
        self.product_repo = ProductRepository(session)

    # ── Category ──────────────────────────────────────────────────────────────

    async def create_category(self, data: CategoryCreate) -> CategoryModel:
        return await self.category_repo.create(data)

    async def get_category_by_id(self, category_id: UUID) -> CategoryModel:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryModel:
        category = await self.get_category_by_id(category_id)
        return await self.category_repo.update(category, data)

    async def delete_category(self, category_id: UUID) -> None:
        category = await self.get_category_by_id(category_id)
        await self.category_repo.delete(category)

    # ── Product ───────────────────────────────────────────────────────────────

    async def create_product(self, data: ProductCreate) -> ProductModel:
        # Verify category exists before creating the product
        await self.get_category_by_id(data.category_id)
        product = await self.product_repo.create(data)
        return await self.product_repo.get_by_id(product.id)

    async def get_product_by_id(self, product_id: UUID) -> ProductModel:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product

    async def update_product(self, product_id: UUID, data: ProductUpdate) -> ProductModel:
        product = await self.get_product_by_id(product_id)
        if data.category_id is not None:
            await self.get_category_by_id(data.category_id)
        return await self.product_repo.update(product, data)

    async def delete_product(self, product_id: UUID) -> None:
        product = await self.get_product_by_id(product_id)
        await self.product_repo.delete(product)
