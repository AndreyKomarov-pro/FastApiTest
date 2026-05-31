import logging
from uuid import UUID

from src.cache.redis_client import RedisClient
from src.enums.order_status import OrderStatus
from src.exceptions import NotFoundException
from src.models.order import OrderModel
from src.models.order_entry import OrderEntryModel
from src.repositories.orders_repository import OrdersRepository
from src.schemas.order import OrderCreate, OrderUpdate, OrderUpdateBody, OrderResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)

ORDERS_LIST_KEY = "orders:page:{page}:size:{size}"
ORDER_KEY = "order:{order_id}"


class OrdersService:
    def __init__(self, repo: OrdersRepository, cache: RedisClient) -> None:
        self.repo = repo
        self.cache = cache

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
        await self.cache.delete_cached_pattern("orders:*")
        return OrderResponse.from_model(result)

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> OrderResponse:
        logger.info("Updating order id=%s", order_id)
        order = await self._get_order_orm(order_id)
        self._update_fields(order, data.body)
        result = await self.repo.update(order)
        await self.cache.delete_cached_pattern("orders:*")
        await self.cache.delete_cached(ORDER_KEY.format(order_id=order_id))
        return OrderResponse.from_model(result)

    async def delete_order(self, order_id: UUID) -> None:
        logger.info("Deleting order id=%s", order_id)
        order = await self._get_order_orm(order_id)
        await self.repo.delete(order)
        await self.cache.delete_cached_pattern("orders:*")
        await self.cache.delete_cached(ORDER_KEY.format(order_id=order_id))

    @staticmethod
    def _update_fields(order: OrderModel, fields: OrderUpdateBody) -> None:
        for key, value in fields.model_dump(exclude_unset=True).items():
            setattr(order, key, value)
