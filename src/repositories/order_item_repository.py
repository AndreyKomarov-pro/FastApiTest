from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import OrderEntry, ProductModel


class OrderItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_order_id(self, order_id: UUID) -> list[OrderEntry]:
        result = await self.session.execute(
            select(OrderEntry)
            .where(OrderEntry.order_id == order_id)
            .options(selectinload(OrderEntry.product))
        )
        return list(result.scalars().all())

    async def get_by_id(self, item_id: UUID) -> OrderEntry | None:
        result = await self.session.execute(
            select(OrderEntry)
            .where(OrderEntry.id == item_id)
            .options(
                selectinload(OrderEntry.product).selectinload(ProductModel.category)
            )
        )
        return result.scalar_one_or_none()

    async def create(self, item: OrderEntry) -> OrderEntry:
        self.session.add(item)
        await self.session.flush()
        return item

    async def update(self, item: OrderEntry) -> OrderEntry:
        await self.session.refresh(item)
        return item

    async def delete(self, item: OrderEntry) -> None:
        await self.session.delete(item)
