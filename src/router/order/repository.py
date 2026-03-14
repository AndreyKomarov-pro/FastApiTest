from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models import OrderModel, OrderItemModel, ProductModel


class OrderRepository:
    def __init__(self, session: AsyncSession):
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

    async def create(self, user_id: UUID) -> OrderModel:
        from src.models.order import OrderStatus
        order = OrderModel(user_id=user_id, status=OrderStatus.PENDING, total_amount=0)
        self.session.add(order)
        await self.session.flush()
        return order

    async def update_status(self, order: OrderModel, status) -> OrderModel:
        order.status = status
        await self.session.flush()
        return order

    async def update_total(self, order: OrderModel, total: float) -> None:
        order.total_amount = total
        await self.session.flush()

    async def delete(self, order: OrderModel) -> None:
        await self.session.delete(order)
