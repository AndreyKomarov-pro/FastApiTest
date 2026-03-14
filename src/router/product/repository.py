from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models import ProductModel, CategoryModel


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: UUID) -> ProductModel | None:
        result = await self.session.execute(
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(selectinload(ProductModel.category))
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        description: str | None,
        price: float,
        quantity: int,
        category_id: UUID,
    ) -> ProductModel:
        product = ProductModel(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            category_id=category_id,
        )
        self.session.add(product)
        await self.session.flush()
        return product

    async def update(self, product: ProductModel, **kwargs) -> ProductModel:
        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)
        await self.session.flush()
        return product

    async def delete(self, product: ProductModel) -> None:
        await self.session.delete(product)
