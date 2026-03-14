from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.database import get_session
from src.schemas.order_item import OrderItemCreate, OrderItemUpdate, OrderItemResponse
from src.router.order_item.service import OrderItemService

router = APIRouter(prefix="/order-items", tags=["Order Items"])


@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def create_order_item(
    order_id: UUID,
    data: OrderItemCreate,
    session: AsyncSession = Depends(get_session),
):
    service = OrderItemService(session)
    item = await service.create(order_id, data)
    return OrderItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=OrderItemResponse)
async def get_order_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = OrderItemService(session)
    item = await service.get(item_id)
    return OrderItemResponse.model_validate(item)


@router.patch("/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: UUID,
    data: OrderItemUpdate,
    session: AsyncSession = Depends(get_session),
):
    service = OrderItemService(session)
    item = await service.update(item_id, data)
    return OrderItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = OrderItemService(session)
    await service.delete(item_id)
