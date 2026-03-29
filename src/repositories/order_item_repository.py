from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import OrderItemModel, ProductModel, OrderModel


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
        result = await self.session.execute(
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(selectinload(ProductModel.category))
        )
        return result.scalar_one_or_none()

    async def get_order(self, order_id: UUID) -> OrderModel | None:
        return await self.session.get(OrderModel, order_id)

    async def create(self, item: OrderItemModel) -> OrderItemModel:
        self.session.add(item)
        await self.session.flush()
        return item

    async def update(self, item: OrderItemModel) -> OrderItemModel:
        await self.session.flush()
        await self.session.refresh(item)
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
