from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.dependencies.orders import get_orders_service
from src.schemas.orders import OrderItemCreate, OrderItemUpdate, OrderItemResponse
from src.services.orders_service import OrdersService

router = APIRouter(tags=["Order Items"])


@router.post(
    "/orders/{order_id}/items",
    response_model=OrderItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_item(
    order_id: UUID,
    data: OrderItemCreate,
    service: OrdersService = Depends(get_orders_service),
) -> OrderItemResponse:
    return await service.create_order_item(order_id, data)


@router.get("/order-items/{item_id}", response_model=OrderItemResponse)
async def get_order_item(
    item_id: UUID,
    service: OrdersService = Depends(get_orders_service),
) -> OrderItemResponse:
    return await service.get_order_item_by_id(item_id)


@router.patch("/order-items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: UUID,
    data: OrderItemUpdate,
    service: OrdersService = Depends(get_orders_service),
) -> OrderItemResponse:
    return await service.update_order_item(item_id, data)


@router.delete("/order-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(
    item_id: UUID,
    service: OrdersService = Depends(get_orders_service),
) -> None:
    await service.delete_order_item(item_id)
