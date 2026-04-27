from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import CategoryModel, ProductModel


class CatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_categories(self, limit: int, offset: int) -> list[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel)
            .order_by(CategoryModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def create_category(self, category: CategoryModel) -> CategoryModel:
        self.session.add(category)
        await self.session.flush()
        return category

    async def get_products_by_category(self, category_id: UUID, limit: int, offset: int) -> list[ProductModel]:
        result = await self.session.execute(
            select(ProductModel)
            .where(ProductModel.category_id == category_id)
            .options(selectinload(ProductModel.category))
            .order_by(ProductModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def create_product(self, product: ProductModel) -> ProductModel:
        self.session.add(product)
        await self.session.flush()
        return product
