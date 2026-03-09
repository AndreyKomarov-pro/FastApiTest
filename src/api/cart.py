from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from src.models import CartModel
from src.database import get_session
from src.schemas.cart import CartCreate, CartResponse


router = APIRouter(prefix="/carts", tags=["Carts"])


async def get_cart_with_relations(cart_id: UUID, session: AsyncSession) -> CartModel:
    """Вспомогательная функция — загружает корзину со всеми связями"""
    result = await session.execute(
        select(CartModel)
        .where(CartModel.id == cart_id)
        .options(
            selectinload(CartModel.user),
            selectinload(CartModel.products),
        )
    )
    return result.scalar_one_or_none()


@router.post("/", response_model=CartResponse)
async def create_cart(
    cart_data: CartCreate,
    session: AsyncSession = Depends(get_session),
):
    existing = await session.execute(
        select(CartModel).where(CartModel.user_id == cart_data.user_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already has a cart")

    cart = CartModel(**cart_data.model_dump())
    session.add(cart)
    await session.flush()
    await session.commit()

    # после commit загружаем заново со связями
    cart = await get_cart_with_relations(cart.id, session)
    return cart


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(
    cart_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    cart = await get_cart_with_relations(cart_id, session)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@router.put("/{cart_id}", response_model=CartResponse)
async def update_cart(
    cart_id: UUID,
    cart_data: CartCreate,
    session: AsyncSession = Depends(get_session),
):
    cart = await session.get(CartModel, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    if cart_data.user_id != cart.user_id:
        existing = await session.execute(
            select(CartModel).where(CartModel.user_id == cart_data.user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Target user already has a cart")

    cart.user_id = cart_data.user_id
    await session.commit()

    cart = await get_cart_with_relations(cart_id, session)
    return cart


@router.delete("/{cart_id}")
async def delete_cart(
    cart_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    cart = await session.get(CartModel, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    await session.delete(cart)
    await session.commit()
    return {"message": "Cart deleted successfully"}