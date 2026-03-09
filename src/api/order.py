from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from src.models import OrderModel, UserModel, OrderItemModel, ProductModel
from src.models.order import OrderStatus
from src.database import get_session
from src.schemas.order import OrderCreate, OrderResponse


router = APIRouter(prefix="/orders", tags=["Orders"])


async def get_order_with_relations(order_id: UUID, session: AsyncSession) -> OrderModel:
    result = await session.execute(
        select(OrderModel)
        .where(OrderModel.id == order_id)
        .options(
            selectinload(OrderModel.user),
            selectinload(OrderModel.items).selectinload(OrderItemModel.product).selectinload(ProductModel.category),
        )
    )
    return result.scalar_one_or_none()


@router.post("/", response_model=OrderResponse)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(UserModel, data.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    order = OrderModel(user_id=data.user_id, status=OrderStatus.PENDING)
    session.add(order)
    await session.flush()

    for item_data in data.items:
        product = await session.get(ProductModel, item_data.product_id)
        if not product:
            raise HTTPException(status_code=400, detail="Product not found")
        session.add(OrderItemModel(
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=product.price,
        ))

    await session.commit()

    order = await get_order_with_relations(order.id, session)
    return order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    order = await get_order_with_relations(order_id, session)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    order_data: OrderCreate,
    session: AsyncSession = Depends(get_session),
):
    order = await session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order_data.user_id != order.user_id:
        user = await session.get(UserModel, order_data.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

    order.user_id = order_data.user_id
    await session.commit()

    order = await get_order_with_relations(order_id, session)
    return order


@router.delete("/{order_id}")
async def delete_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    order = await session.get(OrderModel, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await session.delete(order)
    await session.commit()
    return {"message": "Order deleted successfully"}