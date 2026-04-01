from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import OrderModel, OrderLineModel, ProductModel


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
                .selectinload(OrderLineModel.product)
                .selectinload(ProductModel.category),
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int, offset: int) -> list[OrderModel]:
        result = await self.session.execute(
            select(OrderModel)
            .options(
                selectinload(OrderModel.user),
                selectinload(OrderModel.items)
                .selectinload(OrderLineModel.product)
                .selectinload(ProductModel.category),
            )
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .with_for_update(skip_locked=True)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(OrderModel))
        return result.scalar_one()

    async def create(self, order: OrderModel) -> OrderModel:
        self.session.add(order)
        await self.session.flush()
        return order

    async def update(self, order: OrderModel) -> OrderModel:
        await self.session.flush()
        await self.session.refresh(order)
        return order

    async def update_total(self, order: OrderModel, total: Decimal) -> None:
        order.total_amount = total
        await self.session.flush()

    async def delete(self, order: OrderModel) -> None:
        await self.session.delete(order)
