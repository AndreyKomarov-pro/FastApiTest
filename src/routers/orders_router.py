from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.dependencies.orders import get_orders_service
from src.schemas.orders import OrderCreate, OrderItemCreate, OrderItemResponse, OrderResponse
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


@router.get("/orders/{order_id}/items", response_model=list[OrderItemResponse])
async def list_order_items(
    order_id: UUID,
    service: OrdersService = Depends(get_orders_service),
) -> list[OrderItemResponse]:
    return await service.get_order_items(order_id)


@router.post("/orders/{order_id}/items", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def add_order_item(
    order_id: UUID,
    data: OrderItemCreate,
    service: OrdersService = Depends(get_orders_service),
) -> OrderItemResponse:
    return await service.add_item_to_order(order_id, data)
