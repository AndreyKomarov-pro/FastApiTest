from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.pagination import PageResponse
from src.schemas.users_schemas import (
    UserCreate, UserUpdate, UserResponse,
    CartCreate, CartResponse,
)
from src.services.users_service import UsersService

router = APIRouter(tags=["Users"])


def get_service(session: AsyncSession = Depends(get_db)) -> UsersService:
    return UsersService(session)


@router.get("/users/", response_model=PageResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: UsersService = Depends(get_service),
) -> PageResponse[UserResponse]:
    return await service.get_users(page, size)


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: UsersService = Depends(get_service),
) -> UserResponse:
    return await service.create_user(data)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    service: UsersService = Depends(get_service),
) -> UserResponse:
    return await service.get_user_by_id(user_id)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UsersService = Depends(get_service),
) -> UserResponse:
    return await service.update_user(user_id, data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: UsersService = Depends(get_service),
) -> None:
    await service.delete_user(user_id)


@router.post("/users/{user_id}/cart", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(
    user_id: UUID,
    data: CartCreate,
    service: UsersService = Depends(get_service),
) -> CartResponse:
    return await service.create_cart(user_id, data)


@router.get("/users/{user_id}/cart", response_model=CartResponse)
async def get_cart(
    user_id: UUID,
    service: UsersService = Depends(get_service),
) -> CartResponse:
    return await service.get_cart(user_id)


@router.delete("/users/{user_id}/cart", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    user_id: UUID,
    service: UsersService = Depends(get_service),
) -> None:
    await service.delete_cart(user_id)
