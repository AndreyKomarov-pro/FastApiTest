import json
import logging
from decimal import Decimal
from uuid import UUID, uuid4

from src.cache.redis_client import RedisClient
from src.clients.product_info_client import ProductInfoClient
from src.enums.category_status import CategoryStatus
from src.exceptions import NotFoundException
from src.exceptions.service_unavailable import ServiceUnavailableException
from src.models.category import CategoryModel
from src.models.product import ProductModel
from src.repositories.category_repository import CategoryRepository
from src.schemas.catalog import (
    CategoryCreate,
    CategoryUpdate,
    CategoryUpdateBody,
    CategoryResponse,
    EnrichedCategoryResponse,
)
from src.schemas.pagination import PageResponse
from src.schemas.product_info import ProductInfoBody

logger = logging.getLogger(__name__)

CATEGORIES_LIST_KEY = "categories:page:{page}:size:{size}"
CATEGORY_KEY = "category:{category_id}"


class CategoryService:
    def __init__(
        self,
        repo: CategoryRepository,
        cache: RedisClient,
        product_info_client: ProductInfoClient,
    ) -> None:
        self.repo = repo
        self.cache = cache
        self.product_info_client = product_info_client

    async def _get_category_orm(self, category_id: UUID) -> CategoryModel:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    async def get_categories(self, page: int, size: int) -> PageResponse[CategoryResponse]:
        logger.debug("Listing categories page=%s size=%s", page, size)
        cache_key = CATEGORIES_LIST_KEY.format(page=page, size=size)
        cached = await self.cache.get_cached(cache_key)
        if cached:
            return PageResponse[CategoryResponse].model_validate(cached)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        result = PageResponse(
            items=CategoryResponse.from_list(items),
            page=page,
            size=size,
        )
        await self.cache.set_cached(cache_key, result.model_dump(mode="json"))
        return result

    async def get_category_by_id(self, category_id: UUID) -> EnrichedCategoryResponse:
        logger.debug("Fetching category id=%s", category_id)
        cache_key = CATEGORY_KEY.format(category_id=category_id)
        cached = await self.cache.get_cached(cache_key)
        if cached:
            return EnrichedCategoryResponse.model_validate(cached)
        category = await self._get_category_orm(category_id)
        product_infos = {}
        for product in category.products:
            info = await self.product_info_client.get_product_info(str(product.id))
            product_infos[str(product.id)] = info
        enriched = EnrichedCategoryResponse.from_model(category, product_infos)
        await self.cache.set_cached(cache_key, enriched.model_dump(mode="json"))
        return enriched

    async def create_category(self, data: CategoryCreate) -> CategoryResponse:
        logger.info("Creating category name=%s", data.body.name)
        idempotency_key = uuid4()
        category = CategoryModel(
            name=data.body.name,
            description=data.body.description,
            status=CategoryStatus.PENDING,
            idempotency_key=idempotency_key,
        )
        category.products = [
            ProductModel(
                name=p.name,
                description=p.description,
                price=p.price,
                quantity=p.quantity,
            )
            for p in data.body.products
        ]
        result = await self.repo.create(category)
        payload = [
            ProductInfoBody(
                product_id=product.id,
                rating=Decimal("0"),
                reviews_count=0,
                warehouse_stock=product.quantity,
                idempotency_key=idempotency_key,
            ).model_dump(mode="json")
            for product in result.products
        ]
        result.payload_json = json.dumps(payload)
        await self.repo.update(result)

        try:
            for item in payload:
                await self.product_info_client.create_product_info(
                    ProductInfoBody.model_validate(item)
                )
            await self.repo.update_status(
                result.id, CategoryStatus.CONFIRMED, expected_status=CategoryStatus.PENDING
            )
            result.status = CategoryStatus.CONFIRMED
        except ServiceUnavailableException:
            logger.warning("External service unavailable, category %s stays PENDING", result.id)
        except Exception:
            await self.repo.update_status(
                result.id, CategoryStatus.ERROR, expected_status=CategoryStatus.PENDING,
                last_error="Unexpected error during product info creation",
            )
            raise

        return CategoryResponse.from_model(result)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryResponse:
        logger.info("Updating category id=%s", category_id)
        category = await self._get_category_orm(category_id)
        self._update_fields(category, data.body)
        result = await self.repo.update(category)
        await self.cache.delete_cached_pattern("categories:*")
        await self.cache.delete_cached(CATEGORY_KEY.format(category_id=category_id))
        return CategoryResponse.from_model(result)

    async def delete_category(self, category_id: UUID) -> None:
        logger.info("Deleting category id=%s", category_id)
        category = await self._get_category_orm(category_id)
        await self.repo.delete(category)
        await self.cache.delete_cached_pattern("categories:*")
        await self.cache.delete_cached(CATEGORY_KEY.format(category_id=category_id))

    @staticmethod
    def _update_fields(category: CategoryModel, fields: CategoryUpdateBody) -> None:
        for key, value in fields.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
