from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import ProductModel


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, product_id: UUID) -> ProductModel | None:
        result = await self.session.execute(
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(selectinload(ProductModel.category))
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int, offset: int) -> list[ProductModel]:
        result = await self.session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.category))
            .order_by(ProductModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .with_for_update(skip_locked=True)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(ProductModel))
        return result.scalar_one()

    async def create(self, product: ProductModel) -> ProductModel:
        self.session.add(product)
        await self.session.flush()
        return product

    async def update(self, product: ProductModel) -> ProductModel:
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def delete(self, product: ProductModel) -> None:
        await self.session.delete(product)
