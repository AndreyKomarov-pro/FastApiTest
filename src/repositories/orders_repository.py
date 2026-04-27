from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models import OrderModel, OrderEntry


class OrdersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[OrderModel]:
        order_ids_cte = (
            select(OrderModel.id)
            .where(OrderModel.is_deleted == False)
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .cte("target_orders")
        )

        result = await self.session.execute(
            select(OrderModel)
            .join(order_ids_cte, OrderModel.id == order_ids_cte.c.id)
            .options(
                joinedload(OrderModel.user),
                joinedload(OrderModel.items).joinedload(OrderEntry.product),
            )
            .order_by(OrderModel.created_at.desc())
        )
        return list(result.unique().scalars().all())

    async def get_by_id(self, order_id: UUID) -> OrderModel | None:
        order_cte = (
            select(OrderModel.id)
            .where(OrderModel.id == order_id, OrderModel.is_deleted == False)
            .cte("target_order")
        )

        result = await self.session.execute(
            select(OrderModel)
            .join(order_cte, OrderModel.id == order_cte.c.id)
            .options(
                joinedload(OrderModel.user),
                joinedload(OrderModel.items).joinedload(OrderEntry.product),
            )
        )
        return result.unique().scalar_one_or_none()

    async def create(self, order: OrderModel) -> OrderModel:
        self.session.add(order)
        await self.session.flush()
        return order

    async def create_item(self, item: OrderEntry) -> OrderEntry:
        self.session.add(item)
        await self.session.flush()
        return item

    async def update(self, order: OrderModel) -> OrderModel:
        await self.session.refresh(order)
        return order

    async def delete(self, order: OrderModel) -> None:
        order.is_deleted = True
