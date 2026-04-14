from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.dependencies.orders import get_orders_service
from src.schemas.orders import OrderCreate, OrderUpdate, OrderResponse
from src.schemas.pagination import PageResponse
from src.services.orders_service import OrdersService

router = APIRouter(tags=["Orders"])


@router.get("/orders/", response_model=PageResponse[OrderResponse])
async def list_orders(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: OrdersService = Depends(get_orders_service),
) -> PageResponse[OrderResponse]:
    return await service.get_orders(page, size)


@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    service: OrdersService = Depends(get_orders_service),
) -> OrderResponse:
    return await service.create_order(data)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    service: OrdersService = Depends(get_orders_service),
) -> OrderResponse:
    return await service.get_order_by_id(order_id)


@router.patch("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    service: OrdersService = Depends(get_orders_service),
) -> OrderResponse:
    return await service.update_order(order_id, data)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    service: OrdersService = Depends(get_orders_service),
) -> None:
    await service.delete_order(order_id)
