from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models import OrderItemModel, OrderModel, ProductModel


class OrderItemRepository:
    def __init__(self, session: AsyncSession):
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

    async def get_order(self, order_id: UUID) -> OrderModel | None:
        return await self.session.get(OrderModel, order_id)

    async def create(self, order_id: UUID, product_id: UUID, quantity: int, price: float) -> OrderItemModel:
        item = OrderItemModel(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def update(self, item: OrderItemModel, quantity: int | None) -> OrderItemModel:
        if quantity is not None:
            item.quantity = quantity
        await self.session.flush()
        return item

    async def recalc_order_total(self, order_id: UUID) -> None:
        result = await self.session.execute(
            select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        )
        items = result.scalars().all()
        order = await self.get_order(order_id)
        if order:
            order.total_amount = float(sum(float(i.price) * i.quantity for i in items))
            await self.session.flush()

    async def delete(self, item: OrderItemModel) -> None:
        await self.session.delete(item)
