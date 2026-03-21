from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException
from src.models import OrderModel, OrderItemModel
from src.router.orders.repository import OrderRepository, OrderItemRepository
from src.router.orders.schemas import OrderCreate, OrderUpdate, OrderItemCreate, OrderItemUpdate


class OrdersService:
    def __init__(self, session: AsyncSession) -> None:
        self.order_repo = OrderRepository(session)
        self.item_repo = OrderItemRepository(session)

    # ── Order ─────────────────────────────────────────────────────────────────

    async def create_order(self, data: OrderCreate) -> OrderModel:
        user = await self.order_repo.get_user(data.user_id)
        if not user:
            raise NotFoundException("User", data.user_id)

        order = await self.order_repo.create(user_id=data.user_id)

        total = await self._add_items_to_order(order.id, data.item_ids)
        await self.order_repo.update_total(order, total)

        return await self.order_repo.get_by_id(order.id)

    async def get_order_by_id(self, order_id: UUID) -> OrderModel:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return order

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> OrderModel:
        order = await self.get_order_by_id(order_id)
        if data.status is not None:
            await self.order_repo.update_status(order, data.status)
        return await self.order_repo.get_by_id(order_id)

    async def delete_order(self, order_id: UUID) -> None:
        order = await self.get_order_by_id(order_id)
        await self.order_repo.delete(order)

    # ── Order Item ─────────────────────────────────────────────────────────────

    async def create_order_item(self, order_id: UUID, data: OrderItemCreate) -> OrderItemModel:
        order = await self.item_repo.get_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)

        product = await self.item_repo.get_product(data.product_id)
        if not product:
            raise NotFoundException("Product", data.product_id)

        item = await self.item_repo.create(
            order_id=order_id,
            product_id=product.id,
            quantity=data.quantity,
            price=Decimal(str(product.price)),
        )
        await self.item_repo.recalc_order_total(order_id)
        return await self.item_repo.get_by_id(item.id)

    async def get_order_item_by_id(self, item_id: UUID) -> OrderItemModel:
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("OrderItem", item_id)
        return item

    async def update_order_item(self, item_id: UUID, data: OrderItemUpdate) -> OrderItemModel:
        item = await self.get_order_item_by_id(item_id)
        await self.item_repo.update(item, data)
        await self.item_repo.recalc_order_total(item.order_id)
        return await self.item_repo.get_by_id(item_id)

    async def delete_order_item(self, item_id: UUID) -> None:
        item = await self.get_order_item_by_id(item_id)
        order_id = item.order_id
        await self.item_repo.delete(item)
        await self.item_repo.recalc_order_total(order_id)

    # ── Helpers ────────────────────────────────────────────────────────────────

    async def _add_items_to_order(
        self, order_id: UUID, items_data: list[OrderItemCreate]
    ) -> Decimal:
        total = Decimal("0")
        for item_data in items_data:
            product = await self.item_repo.get_product(item_data.product_id)
            if not product:
                raise NotFoundException("Product", item_data.product_id)
            price = Decimal(str(product.price))
            await self.item_repo.create(
                order_id=order_id,
                product_id=product.id,
                quantity=item_data.quantity,
                price=price,
            )
            total += price * item_data.quantity
        return total
