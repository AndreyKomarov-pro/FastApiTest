from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.database import get_session
from src.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from src.router.order.service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_session),
):
    service = OrderService(session)
    order = await service.create(data)
    return OrderResponse.model_validate(order)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = OrderService(session)
    order = await service.get(order_id)
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    session: AsyncSession = Depends(get_session),
):
    service = OrderService(session)
    order = await service.update(order_id, data)
    return OrderResponse.model_validate(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = OrderService(session)
    await service.delete(order_id)
