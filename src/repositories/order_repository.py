from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import OrderModel, OrderItemModel, ProductModel, UserModel


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
