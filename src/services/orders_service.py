import logging
from decimal import Decimal
from uuid import UUID

from src.exceptions import NotFoundException
from src.models import OrderModel, ProductModel
from src.models.order_entry import OrderEntry
from src.enums.order_status import OrderStatus
from src.repositories.orders_repository import OrdersRepository
from src.schemas.orders import OrderCreate, OrderUpdate, OrderResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)


class OrdersService:
    def __init__(self, repo: OrdersRepository) -> None:
        self.repo = repo

    async def create_order(self, data: OrderCreate) -> OrderResponse:
        logger.info("Creating order for user_id=%s", data.body.user_id)
        order = OrderModel(user_id=data.body.user_id, status=OrderStatus.PENDING)
        order = await self.repo.create(order)

        for item_data in data.body.item_ids:
            product = await self.repo.get_product(item_data.product_id)
            if not product:
                raise NotFoundException("Product", item_data.product_id)
            item = OrderEntry(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data.quantity,
                price=Decimal(str(product.price)),
            )
            await self.repo.create_item(item)

        result = await self.repo.get_by_id(order.id)
        return OrderResponse.model_validate(result)

    async def get_orders(self, page: int, size: int) -> PageResponse[OrderResponse]:
        logger.debug("Listing orders page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        return PageResponse.build(
            items=[OrderResponse.model_validate(o) for o in items],
            page=page,
            size=size,
        )

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> OrderResponse:
        logger.info("Updating order id=%s", order_id)
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        if data.status is not None:
            order.status = data.status
            await self.repo.update(order)
        result = await self.repo.get_by_id(order_id)
        return OrderResponse.model_validate(result)

    async def delete_order(self, order_id: UUID) -> None:
        logger.info("Deleting order id=%s", order_id)
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        await self.repo.delete(order)
