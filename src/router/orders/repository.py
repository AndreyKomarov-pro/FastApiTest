from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions import NotFoundException
from src.models import OrderModel, OrderItemModel, ProductModel, UserModel
from src.models.order import OrderStatus


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, order_id: UUID) -> OrderModel | None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(
                selectinload(OrderModel.user),
                selectinload(OrderModel.items)
                .selectinload(OrderItemModel.product)
                .selectinload(ProductModel.category),
            )
        )
        return result.scalar_one_or_none()

    async def get_user(self, user_id: UUID) -> UserModel | None:
        return await self.session.get(UserModel, user_id)

    async def create(self, user_id: UUID) -> OrderModel:
        order = OrderModel(user_id=user_id, status=OrderStatus.PENDING, total_amount=0)
        self.session.add(order)
        await self.session.flush()
        return order

    async def update_status(self, order: OrderModel, status: OrderStatus) -> OrderModel:
        order.status = status
        await self.session.flush()
        return order

    async def update_total(self, order: OrderModel, total: Decimal) -> None:
        order.total_amount = total
        await self.session.flush()

    async def delete(self, order: OrderModel) -> None:
        await self.session.delete(order)


class OrderItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: UUID) -> OrderItemModel | None:
        result = await self.session.execute(
            select(OrderItemModel)
            .where(OrderItemModel.id == item_id)
            .options(
                selectinload(OrderItemModel.product).selectinload(ProductModel.category)
            )
        )
        return result.scalar_one_or_none()

    async def get_product(self, product_id: UUID) -> ProductModel | None:
        return await self.session.get(ProductModel, product_id)

    async def get_order(self, order_id: UUID) -> OrderModel | None:
        return await self.session.get(OrderModel, order_id)

    async def create(self, order_id: UUID, product_id: UUID, quantity: int, price: Decimal) -> OrderItemModel:
        item = OrderItemModel(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def update(self, item: OrderItemModel, data) -> OrderItemModel:
        if data.product_id is not None:
            product = await self.get_product(data.product_id)
            if not product:
                raise NotFoundException("Product", data.product_id)
            item.product_id = data.product_id
            item.price = product.price
        if data.quantity is not None:
            item.quantity = data.quantity
        await self.session.flush()
        return item

    async def delete(self, item: OrderItemModel) -> None:
        await self.session.delete(item)

    async def recalc_order_total(self, order_id: UUID) -> None:
        result = await self.session.execute(
            select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        )
        items = result.scalars().all()
        order = await self.get_order(order_id)
        if order:
            order.total_amount = self._calculate_total(items)
            await self.session.flush()

    @staticmethod
    def _calculate_total(items: list[OrderItemModel]) -> Decimal:
        return sum(
            (Decimal(str(item.price)) * item.quantity for item in items),
            Decimal("0"),
        )
