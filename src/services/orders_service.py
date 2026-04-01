import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.enums.order_status import OrderStatus
from src.exceptions import NotFoundException
from src.models import OrderModel, OrderLineModel, ProductModel
from src.repositories.order_repository import OrderRepository
from src.repositories.order_item_repository import OrderItemRepository
from src.schemas.orders_schemas import (
    OrderCreate, OrderUpdate, OrderResponse,
    OrderItemCreate, OrderItemUpdate, OrderItemResponse,
)
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)


class OrdersService:
    def __init__(self, session: AsyncSession) -> None:
        self.order_repo = OrderRepository(session)
        self.item_repo = OrderItemRepository(session)

    @staticmethod
    def _to_order_model(data: OrderCreate) -> OrderModel:
        return OrderModel(user_id=data.user_id, status=OrderStatus.PENDING, total_amount=0)

    @staticmethod
    def _to_order_item_model(order_id: UUID, product: ProductModel, data: OrderItemCreate) -> OrderLineModel:
        return OrderLineModel(
            order_id=order_id,
            product_id=product.id,
            quantity=data.quantity,
            price=Decimal(str(product.price)),
        )

    async def _fetch_order(self, order_id: UUID) -> OrderModel:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return order

    async def _fetch_order_item(self, item_id: UUID) -> OrderLineModel:
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("OrderItem", item_id)
        return item

    async def create_order(self, data: OrderCreate) -> OrderResponse:
        logger.info("Creating order for user_id=%s", data.user_id)
        order = self._to_order_model(data)
        order = await self.order_repo.create(order)

        total = await self._add_items_to_order(order.id, data.item_ids)
        await self.order_repo.update_total(order, total)

        result = await self.order_repo.get_by_id(order.id)
        return OrderResponse.model_validate(result)

    async def get_order_by_id(self, order_id: UUID) -> OrderResponse:
        logger.debug("Fetching order id=%s", order_id)
        order = await self._fetch_order(order_id)
        return OrderResponse.model_validate(order)

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> OrderResponse:
        logger.info("Updating order id=%s", order_id)
        order = await self._fetch_order(order_id)
        if data.status is not None:
            order.status = data.status
            await self.order_repo.update(order)
        result = await self.order_repo.get_by_id(order_id)
        return OrderResponse.model_validate(result)

    async def delete_order(self, order_id: UUID) -> None:
        logger.info("Deleting order id=%s", order_id)
        order = await self._fetch_order(order_id)
        await self.order_repo.delete(order)

    async def get_orders(self, page: int, size: int) -> PageResponse[OrderResponse]:
        logger.debug("Listing orders page=%s size=%s", page, size)
        offset = (page - 1) * size
        items, total = await self.order_repo.get_all(size, offset), await self.order_repo.count()
        return PageResponse.build(
            items=[OrderResponse.model_validate(o) for o in items],
            total=total,
            page=page,
            size=size,
        )

    async def create_order_item(self, order_id: UUID, data: OrderItemCreate) -> OrderItemResponse:
        logger.info("Creating order item order_id=%s product_id=%s", order_id, data.product_id)
        order = await self.item_repo.get_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)

        product = await self.item_repo.get_product(data.product_id)
        if not product:
            raise NotFoundException("Product", data.product_id)

        item = self._to_order_item_model(order_id, product, data)
        item = await self.item_repo.create(item)
        await self.item_repo.recalc_order_total(order_id)
        item.product = product
        return OrderItemResponse.model_validate(item)

    async def get_order_item_by_id(self, item_id: UUID) -> OrderItemResponse:
        logger.debug("Fetching order item id=%s", item_id)
        item = await self._fetch_order_item(item_id)
        return OrderItemResponse.model_validate(item)

    async def update_order_item(self, item_id: UUID, data: OrderItemUpdate) -> OrderItemResponse:
        logger.info("Updating order item id=%s", item_id)
        item = await self._fetch_order_item(item_id)
        if data.product is not None:
            product = await self.item_repo.get_product(data.product.product_id)
            if not product:
                raise NotFoundException("Product", data.product.product_id)
            item.product_id = data.product.product_id
            item.price = product.price
        if data.quantity is not None:
            item.quantity = data.quantity
        await self.item_repo.update(item)
        await self.item_repo.recalc_order_total(item.order_id)
        result = await self.item_repo.get_by_id(item_id)
        return OrderItemResponse.model_validate(result)

    async def delete_order_item(self, item_id: UUID) -> None:
        logger.info("Deleting order item id=%s", item_id)
        item = await self._fetch_order_item(item_id)
        order_id = item.order_id
        await self.item_repo.delete(item)
        await self.item_repo.recalc_order_total(order_id)

    async def _add_items_to_order(
        self, order_id: UUID, items_data: list[OrderItemCreate]
    ) -> Decimal:
        total = Decimal("0")
        for item_data in items_data:
            product = await self.item_repo.get_product(item_data.product_id)
            if not product:
                raise NotFoundException("Product", item_data.product_id)
            item = self._to_order_item_model(order_id, product, item_data)
            await self.item_repo.create(item)
            total += Decimal(str(product.price)) * item_data.quantity
        return total
