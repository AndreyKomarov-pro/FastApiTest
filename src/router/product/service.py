from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import ProductModel, CategoryModel
from src.schemas.product import ProductCreate, ProductUpdate
from src.exceptions import NotFoundException
from src.router.product.repository import ProductRepository
from src.router.category.repository import CategoryRepository


class ProductService:
    def __init__(self, session: AsyncSession):
        self.repo = ProductRepository(session)
        self.category_repo = CategoryRepository(session)

    async def _get_or_create_category(self, category_data) -> CategoryModel:
        category = CategoryModel(
            name=category_data.name,
            description=category_data.description,
        )
        self.category_repo.session.add(category)
        await self.category_repo.session.flush()
        return category

    async def create(self, data: ProductCreate) -> ProductModel:
        category = await self._get_or_create_category(data.category)
        product = await self.repo.create(
            name=data.name,
            description=data.description,
            price=data.price,
            quantity=data.quantity,
            category_id=category.id,
        )
        return await self.repo.get_by_id(product.id)

    async def get(self, product_id: UUID) -> ProductModel:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product

    async def update(self, product_id: UUID, data: ProductUpdate) -> ProductModel:
        product = await self.get(product_id)
        update_kwargs = {}
        if data.name is not None:
            update_kwargs["name"] = data.name
        if data.description is not None:
            update_kwargs["description"] = data.description
        if data.price is not None:
            update_kwargs["price"] = data.price
        if data.quantity is not None:
            update_kwargs["quantity"] = data.quantity
        if data.category is not None:
            category = await self._get_or_create_category(data.category)
            update_kwargs["category_id"] = category.id
        await self.repo.update(product, **update_kwargs)
        return await self.repo.get_by_id(product_id)

    async def delete(self, product_id: UUID) -> None:
        product = await self.get(product_id)
        await self.repo.delete(product)
