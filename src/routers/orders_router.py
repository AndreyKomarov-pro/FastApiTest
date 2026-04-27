from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.orders_repository import OrdersRepository
from src.schemas.orders import OrderCreate, OrderUpdate, OrderResponse
from src.schemas.pagination import PageResponse
from src.services.orders_service import OrdersService

router = APIRouter(tags=["Orders"])


@router.get("/orders/", response_model=PageResponse[OrderResponse])
async def list_orders(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PageResponse[OrderResponse]:
    service = OrdersService(OrdersRepository(session))
    return await service.get_orders(page, size)


@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    service = OrdersService(OrdersRepository(session))
    return await service.create_order(data)


@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    session: AsyncSession = Depends(get_db),
) -> OrderResponse:
    service = OrdersService(OrdersRepository(session))
    return await service.update_order(order_id, data)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    service = OrdersService(OrdersRepository(session))
    await service.delete_order(order_id)
