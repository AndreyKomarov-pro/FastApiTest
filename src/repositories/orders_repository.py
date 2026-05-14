from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.models.order import OrderModel
from src.models.order_item import OrderItem

class OrdersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[OrderModel]:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.is_deleted == False)
            .options(
                joinedload(OrderModel.order_items).joinedload(OrderItem.product)
            )
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.unique().scalars().all())

    async def get_by_id(self, order_id: UUID) -> OrderModel | None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id, OrderModel.is_deleted == False)
            .options(
                joinedload(OrderModel.order_items).joinedload(OrderItem.product)
            )
        )
        return result.unique().scalar_one_or_none()

    async def get_by_id_for_update(self, order_id: UUID) -> OrderModel | None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id, OrderModel.is_deleted == False)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def create(self, order: OrderModel) -> OrderModel:
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order, attribute_names=["order_items"])
        return order

    async def update(self, order: OrderModel) -> OrderModel:
        await self.session.flush()
        await self.session.refresh(order)
        await self.session.refresh(order, attribute_names=["order_items"])
        return order

    async def delete(self, order: OrderModel) -> None:
        order.is_deleted = True
        await self.session.flush()
