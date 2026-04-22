from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.pagination import PageResponse
from src.schemas.users import (
    UserCreate, UserUpdate, UserResponse,
    CartUpdate, CartResponse,
)
from src.services.users_service import UsersService

router = APIRouter(tags=["Users"])


@router.get("/users/", response_model=PageResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PageResponse[UserResponse]:
    service = UsersService(session)
    return await service.get_users(page, size)


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UsersService(session)
    return await service.create_user(data)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UsersService(session)
    return await service.update_user(user_id, data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    service = UsersService(session)
    await service.delete_user(user_id)


@router.get("/users/{user_id}/cart", response_model=CartResponse)
async def get_cart(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> CartResponse:
    service = UsersService(session)
    return await service.get_cart(user_id)


@router.post("/users/{user_id}/cart", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> CartResponse:
    service = UsersService(session)
    return await service.create_cart(user_id)


@router.put("/users/{user_id}/cart", response_model=CartResponse)
async def update_cart(
    user_id: UUID,
    data: CartUpdate,
    session: AsyncSession = Depends(get_db),
) -> CartResponse:
    service = UsersService(session)
    return await service.update_cart(user_id, data)


@router.delete("/users/{user_id}/cart", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    service = UsersService(session)
    await service.delete_cart(user_id)
