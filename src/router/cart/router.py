from fastapi import APIRouter, status
from uuid import UUID

from src.schemas.cart import CartCreate, CartResponse
from src.router.cart.service import CartService

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(data: CartCreate):
    async with CartService() as service:
        cart = await service.create(data)
        return CartResponse.model_validate(cart)


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(cart_id: UUID):
    async with CartService() as service:
        cart = await service.get(cart_id)
        return CartResponse.model_validate(cart)


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(cart_id: UUID):
    async with CartService() as service:
        await service.delete(cart_id)
