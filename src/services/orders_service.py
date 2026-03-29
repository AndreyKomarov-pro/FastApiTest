import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.enums.order_status import OrderStatus
from src.exceptions import NotFoundException
from src.models import OrderModel, OrderItemModel, ProductModel
from src.repositories.order_repository import OrderRepository
from src.repositories.order_item_repository import OrderItemRepository
from src.schemas.orders_schemas import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate

logger = logging.getLogger(__name__)


class OrdersService:
    def __init__(self, session: AsyncSession) -> None:
        self.order_repo = OrderRepository(session)
        self.item_repo = OrderItemRepository(session)

    @staticmethod
    def _to_order_model(data: OrderCreate) -> OrderModel:
        return OrderModel(user_id=data.user_id, status=OrderStatus.PENDING, total_amount=0)

    @staticmethod
    def _to_order_item_model(order_id: UUID, product: ProductModel, data: OrderItemCreate) -> OrderItemModel:
        return OrderItemModel(
            order_id=order_id,
            product_id=product.id,
            quantity=data.quantity,
            price=Decimal(str(product.price)),
        )

    async def create_order(self, data: OrderCreate) -> OrderModel:
        logger.info("Creating order for user_id=%s", data.user_id)
        user = await self.order_repo.get_user(data.user_id)
        if not user:
            raise NotFoundException("User", data.user_id)

        order = self._to_order_model(data)
        order = await self.order_repo.create(order)

        total = await self._add_items_to_order(order.id, data.item_ids)
        await self.order_repo.update_total(order, total)

        return await self.order_repo.get_by_id(order.id)

    async def get_order_by_id(self, order_id: UUID) -> OrderModel:
        logger.debug("Fetching order id=%s", order_id)
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return order

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> OrderModel:
        logger.info("Updating order id=%s", order_id)
        order = await self.get_order_by_id(order_id)
        if data.status is not None:
            order.status = data.status
            await self.order_repo.update(order)
        return await self.order_repo.get_by_id(order_id)

    async def delete_order(self, order_id: UUID) -> None:
        logger.info("Deleting order id=%s", order_id)
        order = await self.get_order_by_id(order_id)
        await self.order_repo.delete(order)

    async def create_order_item(self, order_id: UUID, data: OrderItemCreate) -> OrderItemModel:
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
        return item

    async def get_order_item_by_id(self, item_id: UUID) -> OrderItemModel:
        logger.debug("Fetching order item id=%s", item_id)
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("OrderItem", item_id)
        return item

    async def update_order_item(self, item_id: UUID, data: OrderItemUpdate) -> OrderItemModel:
        logger.info("Updating order item id=%s", item_id)
        item = await self.get_order_item_by_id(item_id)
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
        return await self.item_repo.get_by_id(item_id)

    async def delete_order_item(self, item_id: UUID) -> None:
        logger.info("Deleting order item id=%s", item_id)
        item = await self.get_order_item_by_id(item_id)
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
