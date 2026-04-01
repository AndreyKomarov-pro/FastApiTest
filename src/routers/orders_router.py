from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.orders_schemas import (
    OrderCreate, OrderUpdate, OrderResponse,
    OrderItemCreate, OrderItemUpdate, OrderItemResponse,
)
from src.schemas.pagination import PageResponse
from src.services.orders_service import OrdersService

router = APIRouter(tags=["Orders"])


def get_service(session: AsyncSession = Depends(get_db)) -> OrdersService:
    return OrdersService(session)


@router.get("/orders/", response_model=PageResponse[OrderResponse])
async def list_orders(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: OrdersService = Depends(get_service),
) -> PageResponse[OrderResponse]:
    return await service.get_orders(page, size)


@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    service: OrdersService = Depends(get_service),
) -> OrderResponse:
    return await service.create_order(data)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    service: OrdersService = Depends(get_service),
) -> OrderResponse:
    return await service.get_order_by_id(order_id)


@router.patch("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    service: OrdersService = Depends(get_service),
) -> OrderResponse:
    return await service.update_order(order_id, data)


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
    return await service.create_order_item(order_id, data)


@router.get("/order-items/{item_id}", response_model=OrderItemResponse)
async def get_order_item(
    item_id: UUID,
    service: OrdersService = Depends(get_service),
) -> OrderItemResponse:
    return await service.get_order_item_by_id(item_id)


@router.patch("/order-items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: UUID,
    data: OrderItemUpdate,
    service: OrdersService = Depends(get_service),
) -> OrderItemResponse:
    return await service.update_order_item(item_id, data)


@router.delete("/order-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(
    item_id: UUID,
    service: OrdersService = Depends(get_service),
) -> None:
    await service.delete_order_item(item_id)
