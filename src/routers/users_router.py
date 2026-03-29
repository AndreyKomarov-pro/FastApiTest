from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.users_schemas import (
    UserCreate, UserUpdate, UserResponse,
    CartCreate, CartResponse,
)
from src.services.users_service import UsersService

router = APIRouter(tags=["Users"])


def get_service(session: AsyncSession = Depends(get_db)) -> UsersService:
    return UsersService(session)


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: UsersService = Depends(get_service),
) -> UserResponse:
    user = await service.create_user(data)
    return UserResponse.model_validate(user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    service: UsersService = Depends(get_service),
) -> UserResponse:
    user = await service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UsersService = Depends(get_service),
) -> UserResponse:
    user = await service.update_user(user_id, data)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: UsersService = Depends(get_service),
) -> None:
    await service.delete_user(user_id)


@router.post("/carts/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(
    data: CartCreate,
    service: UsersService = Depends(get_service),
) -> CartResponse:
    cart = await service.create_cart(data)
    return CartResponse.model_validate(cart)


@router.get("/carts/{cart_id}", response_model=CartResponse)
async def get_cart(
    cart_id: UUID,
    service: UsersService = Depends(get_service),
) -> CartResponse:
    cart = await service.get_cart_by_id(cart_id)
    return CartResponse.model_validate(cart)


@router.delete("/carts/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    cart_id: UUID,
    service: UsersService = Depends(get_service),
) -> None:
    await service.delete_cart(cart_id)
