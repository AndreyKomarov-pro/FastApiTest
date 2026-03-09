from fastapi import APIRouter, Depends, HTTPException
from src.models import OrderItemModel, OrderModel, ProductModel
from src.database import get_session
from src.schemas.order_item import OrderItemCreate, OrderItemResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


router = APIRouter(prefix="/order-items", tags=["Order Items"])


async def get_item_with_relations(item_id: UUID, session: AsyncSession) -> OrderItemModel:
    result = await session.execute(
        select(OrderItemModel)
        .where(OrderItemModel.id == item_id)
        .options(
            selectinload(OrderItemModel.product).selectinload(ProductModel.category),
        )
    )
    return result.scalar_one_or_none()


@router.post("/{order_id}/items", response_model=OrderItemResponse)
async def create_order_item(
    order_id: UUID,
    item_data: OrderItemCreate,
    session: AsyncSession = Depends(get_session),
):
    order = await session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")

    product = await session.get(ProductModel, item_data.product_id)
    if not product:
        raise HTTPException(status_code=400, detail="Product not found")

    item = OrderItemModel(
        order_id=order_id,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
        price=product.price,
    )
    session.add(item)
    await session.flush()

    # обновляем сумму заказа
    items_result = await session.execute(
        select(OrderItemModel).where(OrderItemModel.order_id == order_id)
    )
    order.total_amount = sum(i.price * i.quantity for i in items_result.scalars().all())
    await session.commit()

    # возвращаем со связями
    item = await get_item_with_relations(item.id, session)
    return item


@router.get("/{item_id}", response_model=OrderItemResponse)
async def get_order_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    item = await get_item_with_relations(item_id, session)
    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")
    return item


@router.put("/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: UUID,
    item_data: OrderItemCreate,
    session: AsyncSession = Depends(get_session),
):
    item = await session.get(OrderItemModel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")

    item.quantity = item_data.quantity
    item.product_id = item_data.product_id
    await session.flush()

    # обновляем сумму заказа
    items_result = await session.execute(
        select(OrderItemModel).where(OrderItemModel.order_id == item.order_id)
    )
    order = await session.get(OrderModel, item.order_id)
    order.total_amount = sum(i.price * i.quantity for i in items_result.scalars().all())
    await session.commit()

    # возвращаем со связями
    item = await get_item_with_relations(item_id, session)
    return item


@router.delete("/{item_id}")
async def delete_order_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    item = await session.get(OrderItemModel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")

    order_id = item.order_id
    await session.delete(item)
    await session.flush()

    # обновляем сумму заказа
    items_result = await session.execute(
        select(OrderItemModel).where(OrderItemModel.order_id == order_id)
    )
    order = await session.get(OrderModel, order_id)
    order.total_amount = sum(i.price * i.quantity for i in items_result.scalars().all())
    await session.commit()

    return {"message": "Order item deleted successfully"}