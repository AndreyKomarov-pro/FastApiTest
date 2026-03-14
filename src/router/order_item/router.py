from fastapi import APIRouter, status
from uuid import UUID

from src.schemas.order_item import OrderItemCreate, OrderItemUpdate, OrderItemResponse
from src.router.order_item.service import OrderItemService

router = APIRouter(prefix="/order-items", tags=["Order Items"])


@router.post("/{order_id}/items", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def create_order_item(order_id: UUID, data: OrderItemCreate):
    async with OrderItemService() as service:
        item = await service.create(order_id, data)
        return OrderItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=OrderItemResponse)
async def get_order_item(item_id: UUID):
    async with OrderItemService() as service:
        item = await service.get(item_id)
        return OrderItemResponse.model_validate(item)


@router.patch("/{item_id}", response_model=OrderItemResponse)
async def update_order_item(item_id: UUID, data: OrderItemUpdate):
    async with OrderItemService() as service:
        item = await service.update(item_id, data)
        return OrderItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(item_id: UUID):
    async with OrderItemService() as service:
        await service.delete(item_id)
