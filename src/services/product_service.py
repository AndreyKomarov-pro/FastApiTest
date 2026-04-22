import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException
from src.models import ProductModel
from src.repositories.product_repository import ProductRepository
from src.schemas.pagination import PageResponse
from src.schemas.product import ProductCreateBody, ProductUpdate, ProductResponse

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.product_repo = ProductRepository(session)

    async def _fetch_product(self, product_id: UUID) -> ProductModel:
        logger.debug("Fetching product id=%s", product_id)
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product

    async def get_products(self, category_id: UUID, page: int, size: int) -> PageResponse[ProductResponse]:
        logger.debug("Listing products for category_id=%s page=%s size=%s", category_id, page, size)
        offset = (page - 1) * size
        items = await self.product_repo.get_by_category(category_id, size, offset)
        return PageResponse.build(
            items=[ProductResponse.model_validate(p) for p in items],
            page=page,
            size=size,
        )

    async def create_product(self, category_id: UUID, data: ProductCreateBody) -> ProductResponse:
        logger.info("Creating product in category_id=%s name=%s", category_id, data.name)
        product = ProductModel(**data.model_dump(), category_id=category_id)
        product = await self.product_repo.create(product)
        return ProductResponse.model_validate(product)

    async def update_product(self, product_id: UUID, data: ProductUpdate) -> ProductResponse:
        logger.info("Updating product id=%s", product_id)
        product = await self._fetch_product(product_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(product, field, value)
        updated = await self.product_repo.update(product)
        return ProductResponse.model_validate(updated)

    async def delete_product(self, product_id: UUID) -> None:
        logger.info("Deleting product id=%s", product_id)
        product = await self._fetch_product(product_id)
        await self.product_repo.delete(product)
