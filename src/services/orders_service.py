import logging
from datetime import datetime, timezone
from uuid import UUID

from src.cache.redis_client import RedisClient
from src.config import Settings
from src.enums.event_type import EventType
from src.enums.order_status import OrderStatus
from src.exceptions import NotFoundException
from src.models.order import OrderModel
from src.models.order_entry import OrderEntryModel
from src.models.outbox_event import OutboxEventModel
from src.repositories.orders_repository import OrdersRepository
from src.repositories.outbox_repository import OutboxRepository
from src.schemas.event import EventEnvelope
from src.schemas.order import OrderCreate, OrderUpdate, OrderUpdateBody, OrderResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)

settings = Settings()

ORDERS_LIST_KEY = "orders:page:{page}:size:{size}"
ORDER_KEY = "order:{order_id}"
AGGREGATE_TYPE = "order"


class OrdersService:
    def __init__(
        self,
        repo: OrdersRepository,
        cache: RedisClient,
        outbox_repo: OutboxRepository,
    ) -> None:
        self.repo = repo
        self.cache = cache
        self.outbox_repo = outbox_repo

    async def _get_order_orm(self, order_id: UUID) -> OrderModel:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return order

    async def get_orders(self, page: int, size: int) -> PageResponse[OrderResponse]:
        logger.debug("Listing orders page=%s size=%s", page, size)
        cache_key = ORDERS_LIST_KEY.format(page=page, size=size)
        cached = await self.cache.get_cached(cache_key)
        if cached:
            return PageResponse[OrderResponse].model_validate(cached)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        result = PageResponse(
            items=OrderResponse.from_list(items),
            page=page,
            size=size,
        )
        await self.cache.set_cached(cache_key, result.model_dump(mode="json"))
        return result

    async def create_order(self, data: OrderCreate) -> OrderResponse:
        logger.info("Creating order user_id=%s", data.body.user_id)
        order = OrderModel(
            user_id=data.body.user_id,
            status=OrderStatus.PENDING,
        )
        order.order_entries = [
            OrderEntryModel(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in data.body.items
        ]
        result = await self.repo.create(order)

        await self._publish_event(
            event_type=EventType.ORDER_CREATED,
            aggregate_id=result.id,
            data=data.body.model_dump(mode="json"),
        )

        await self.cache.delete_cached_pattern("orders:*")
        return OrderResponse.from_model(result)

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> OrderResponse:
        logger.info("Updating order id=%s", order_id)
        order = await self._get_order_orm(order_id)
        self._update_fields(order, data.body)
        result = await self.repo.update(order)

        await self._publish_event(
            event_type=EventType.ORDER_UPDATED,
            aggregate_id=order_id,
            data=data.body.model_dump(mode="json", exclude_unset=True),
        )

        await self.cache.delete_cached_pattern("orders:*")
        await self.cache.delete_cached(ORDER_KEY.format(order_id=order_id))
        return OrderResponse.from_model(result)

    async def delete_order(self, order_id: UUID) -> None:
        logger.info("Deleting order id=%s", order_id)
        order = await self._get_order_orm(order_id)
        await self.repo.delete(order)

        await self._publish_event(
            event_type=EventType.ORDER_DELETED,
            aggregate_id=order_id,
            data={"order_id": str(order_id)},
        )

        await self.cache.delete_cached_pattern("orders:*")
        await self.cache.delete_cached(ORDER_KEY.format(order_id=order_id))

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
            topic=settings.kafka_topic_orders,
            payload=envelope.model_dump_json(),
        )
        await self.outbox_repo.create(outbox_event)

    @staticmethod
    def _update_fields(order: OrderModel, fields: OrderUpdateBody) -> None:
        for key, value in fields.model_dump(exclude_unset=True).items():
            setattr(order, key, value)
