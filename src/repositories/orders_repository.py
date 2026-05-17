from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.models.order import OrderModel
from src.models.order_item import OrderEntryModel

class OrdersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[OrderModel]:
        subquery = (
            select(OrderModel.id)
            .where(OrderModel.is_deleted == False)
            .order_by(OrderModel.created_at.desc())
            .with_for_update(skip_locked=True)
            .offset(offset)
            .limit(limit)
        ).subquery()

        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id.in_(select(subquery.c.id)))
            .options(
                joinedload(OrderModel.order_items).joinedload(OrderEntryModel.product)
            )
            .order_by(OrderModel.created_at.desc())
        )
        return list(result.unique().scalars().all())

    async def get_by_id(self, order_id: UUID) -> OrderModel | None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id, OrderModel.is_deleted == False)
            .options(
                joinedload(OrderModel.order_items).joinedload(OrderEntryModel.product)
            )
        )
        return result.unique().scalar_one_or_none()

    async def get_by_id_for_update(self, order_id: UUID) -> OrderModel | None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id, OrderModel.is_deleted == False)
            .options(
                joinedload(OrderModel.order_items).joinedload(OrderEntryModel.product)
            )
            .with_for_update()
        )
        return result.unique().scalar_one_or_none()

    async def create(self, order: OrderModel) -> OrderModel:
        self.session.add(order)
        await self.session.flush()
        await self.session.refresh(order, attribute_names=["order_items"])
        return order

    async def update(self, order: OrderModel) -> OrderModel:
        await self.session.flush()
        await self.session.refresh(order, attribute_names=["order_items", "updated_at"])
        return order

    async def delete(self, order: OrderModel) -> None:
        order.is_deleted = True
        await self.session.flush()
