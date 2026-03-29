from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.orders_schemas import (
    OrderCreate, OrderUpdate, OrderResponse,
    OrderItemCreate, OrderItemUpdate, OrderItemResponse,
)
from src.services.orders_service import OrdersService

router = APIRouter(tags=["Orders"])


def get_service(session: AsyncSession = Depends(get_db)) -> OrdersService:
    return OrdersService(session)


@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    service: OrdersService = Depends(get_service),
) -> OrderResponse:
    order = await service.create_order(data)
    return OrderResponse.model_validate(order)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    service: OrdersService = Depends(get_service),
) -> OrderResponse:
    order = await service.get_order_by_id(order_id)
    return OrderResponse.model_validate(order)


@router.patch("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    service: OrdersService = Depends(get_service),
) -> OrderResponse:
    order = await service.update_order(order_id, data)
    return OrderResponse.model_validate(order)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    service: OrdersService = Depends(get_service),
) -> None:
    await service.delete_order(order_id)


@router.post(
    "/orders/{order_id}/items",
    response_model=OrderItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_item(
    order_id: UUID,
    data: OrderItemCreate,
    service: OrdersService = Depends(get_service),
) -> OrderItemResponse:
    item = await service.create_order_item(order_id, data)
    return OrderItemResponse.model_validate(item)


@router.get("/order-items/{item_id}", response_model=OrderItemResponse)
async def get_order_item(
    item_id: UUID,
    service: OrdersService = Depends(get_service),
) -> OrderItemResponse:
    item = await service.get_order_item_by_id(item_id)
    return OrderItemResponse.model_validate(item)


@router.patch("/order-items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: UUID,
    data: OrderItemUpdate,
    service: OrdersService = Depends(get_service),
) -> OrderItemResponse:
    item = await service.update_order_item(item_id, data)
    return OrderItemResponse.model_validate(item)


@router.delete("/order-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(
    item_id: UUID,
    service: OrdersService = Depends(get_service),
) -> None:
    await service.delete_order_item(item_id)
