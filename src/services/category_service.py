import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from src.cache.redis_client import RedisClient
from src.clients.product_info_client import ProductInfoClient
from src.config import Settings
from src.enums.category_status import CategoryStatus
from src.enums.event_type import EventType
from src.exceptions import NotFoundException
from src.models.category import CategoryModel
from src.models.outbox_event import OutboxEventModel
from src.models.product import ProductModel
from src.repositories.category_repository import CategoryRepository
from src.repositories.outbox_repository import OutboxRepository
from src.schemas.catalog import (
    CategoryCreate,
    CategoryUpdate,
    CategoryUpdateBody,
    CategoryResponse,
    EnrichedCategoryResponse,
)
from src.schemas.event import EventEnvelope
from src.schemas.pagination import PageResponse
from src.schemas.product_info import ProductInfoBody

logger = logging.getLogger(__name__)

settings = Settings()

CATEGORIES_LIST_KEY = "categories:page:{page}:size:{size}"
CATEGORY_KEY = "category:{category_id}"
AGGREGATE_TYPE = "category"


class CategoryService:
    def __init__(
        self,
        repo: CategoryRepository,
        cache: RedisClient,
        product_info_client: ProductInfoClient,
        outbox_repo: OutboxRepository,
    ) -> None:
        self.repo = repo
        self.cache = cache
        self.product_info_client = product_info_client
        self.outbox_repo = outbox_repo

    async def _get_category_orm(self, category_id: UUID) -> CategoryModel:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    async def _get_category_orm_for_update(self, category_id: UUID) -> CategoryModel:
        category = await self.repo.get_by_id_for_update(category_id)
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
        category = data.body.to_model(
            status=CategoryStatus.PENDING,
            idempotency_key=idempotency_key,
        )
        result = await self.repo.create(category)
        payload = self._build_payload(result.products, idempotency_key)
        result.payload_json = json.dumps(payload)
        await self.repo.update(result)

        await self._publish_event(
            event_type=EventType.CATEGORY_CREATED,
            aggregate_id=result.id,
            data=data.body.model_dump(mode="json"),
        )

        return CategoryResponse.from_model(result)

    async def update_category(self, category_id: UUID, data: CategoryUpdate) -> CategoryResponse:
        logger.info("Updating category id=%s", category_id)
        category = await self._get_category_orm(category_id)
        self._update_fields(category, data.body)
        result = await self.repo.update(category)

        await self._publish_event(
            event_type=EventType.CATEGORY_UPDATED,
            aggregate_id=category_id,
            data=data.body.model_dump(mode="json", exclude_unset=True),
        )

        await self._invalidate_category_cache(category_id)
        return CategoryResponse.from_model(result)

    async def delete_category(self, category_id: UUID) -> None:
        logger.info("Deleting category id=%s", category_id)
        category = await self._get_category_orm_for_update(category_id)
        await self.repo.delete(category)

        await self._publish_event(
            event_type=EventType.CATEGORY_DELETED,
            aggregate_id=category_id,
            data={"category_id": str(category_id)},
        )

        await self._invalidate_category_cache(category_id)

    async def _invalidate_category_cache(self, category_id: UUID) -> None:
        await self.cache.delete_cached_pattern("categories:*")
        await self.cache.delete_cached(CATEGORY_KEY.format(category_id=category_id))

    async def _publish_event(
        self,
        event_type: EventType,
        aggregate_id: UUID,
        data: dict,
    ) -> None:
        envelope = EventEnvelope(
            event_id=aggregate_id,
            event_type=event_type,
            aggregate_type=AGGREGATE_TYPE,
            aggregate_id=aggregate_id,
            timestamp=datetime.now(timezone.utc),
            data=data,
        )
        outbox_event = OutboxEventModel(
            aggregate_type=AGGREGATE_TYPE,
            aggregate_id=aggregate_id,
            event_type=event_type,
            topic=settings.kafka_topic_categories,
            payload=envelope.model_dump_json(),
        )
        await self.outbox_repo.create(outbox_event)

    @staticmethod
    def _build_payload(products: list[ProductModel], idempotency_key: UUID) -> list[dict]:
        return [
            ProductInfoBody(
                product_id=product.id,
                rating=Decimal("0"),
                reviews_count=0,
                warehouse_stock=product.quantity,
                idempotency_key=idempotency_key,
            ).model_dump(mode="json")
            for product in products
        ]

    @staticmethod
    def _update_fields(category: CategoryModel, fields: CategoryUpdateBody) -> None:
        for key, value in fields.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
