from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import CategoryModel, ProductModel
from src.router.catalog.schemas import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, category_id: UUID) -> CategoryModel | None:
        return await self.session.get(CategoryModel, category_id)

    async def create(self, data: CategoryCreate) -> CategoryModel:
        category = CategoryModel(name=data.name, description=data.description)
        self.session.add(category)
        await self.session.flush()
        return category

    async def update(self, category: CategoryModel, data: CategoryUpdate) -> CategoryModel:
        if data.name is not None:
            category.name = data.name
        if data.description is not None:
            category.description = data.description
        await self.session.flush()
        return category

    async def delete(self, category: CategoryModel) -> None:
        await self.session.delete(category)


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

    async def create(self, data: ProductCreate) -> ProductModel:
        product = ProductModel(
            name=data.name,
            description=data.description,
            price=data.price,
            quantity=data.quantity,
            category_id=data.category_id,
        )
        self.session.add(product)
        await self.session.flush()
        return product

    async def update(self, product: ProductModel, data: ProductUpdate) -> ProductModel:
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
        await self.session.flush()
        return product

    async def delete(self, product: ProductModel) -> None:
        await self.session.delete(product)
