from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import OrderModel, OrderEntry, ProductModel


class OrdersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[OrderModel]:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.is_deleted == False)
            .options(
                selectinload(OrderModel.user),
                selectinload(OrderModel.items)
                .selectinload(OrderEntry.product),
            )
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id(self, order_id: UUID) -> OrderModel | None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id, OrderModel.is_deleted == False)
            .options(
                selectinload(OrderModel.user),
                selectinload(OrderModel.items)
                .selectinload(OrderEntry.product),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, order: OrderModel) -> OrderModel:
        self.session.add(order)
        await self.session.flush()
        return order

    async def create_item(self, item: OrderEntry) -> OrderEntry:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_product(self, product_id: UUID) -> ProductModel | None:
        return await self.session.get(ProductModel, product_id)

    async def update(self, order: OrderModel) -> OrderModel:
        await self.session.refresh(order)
        return order

    async def delete(self, order: OrderModel) -> None:
        order.is_deleted = True
