from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.database import get_session
from src.schemas.cart import CartCreate, CartResponse
from src.router.cart.service import CartService

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(
    data: CartCreate,
    session: AsyncSession = Depends(get_session),
):
    service = CartService(session)
    cart = await service.create(data)
    return CartResponse.model_validate(cart)


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(
    cart_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = CartService(session)
    cart = await service.get(cart_id)
    return CartResponse.model_validate(cart)


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    cart_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    service = CartService(session)
    await service.delete(cart_id)
