import logging
from uuid import UUID
from src.exceptions import NotFoundException
from src.models.order import OrderModel
from src.repositories.orders_repository import OrdersRepository
from src.schemas.order import OrderCreate, OrderUpdate, OrderUpdateBody, OrderResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)

class OrdersService:
    def __init__(self, repo: OrdersRepository) -> None:
        self.repo = repo

    async def _get_order_orm(self, order_id: UUID) -> OrderModel:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return order

    async def get_orders(self, page: int, size: int) -> PageResponse[OrderResponse]:
        logger.debug("Listing orders page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        return PageResponse(
            items=OrderResponse.from_list(items),
            page=page,
            size=size,
        )

    async def create_order(self, data: OrderCreate) -> OrderResponse:
        logger.info("Creating order user_id=%s", data.body.user_id)
        order = data.body.to_model()
        result = await self.repo.create(order)
        return OrderResponse.from_model(result)

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> OrderResponse:
        logger.info("Updating order id=%s", order_id)
        order = await self._get_order_orm(order_id)
        self._update_fields(order, data.body)
        result = await self.repo.update(order)
        return OrderResponse.from_model(result)

    async def delete_order(self, order_id: UUID) -> None:
        logger.info("Deleting order id=%s", order_id)
        order = await self._get_order_orm(order_id)
        await self.repo.delete(order)

    @staticmethod
    def _update_fields(order: OrderModel, fields: OrderUpdateBody) -> None:
        for key, value in fields.model_dump(exclude_unset=True).items():
            setattr(order, key, value)
