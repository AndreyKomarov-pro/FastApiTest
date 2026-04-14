from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.dependencies.users import get_users_service
from src.schemas.pagination import PageResponse
from src.schemas.users import (
    UserCreate, UserResponse,
    CartCreate, CartResponse,
)
from src.services.users_service import UsersService

router = APIRouter(tags=["Users"])


@router.get("/users/", response_model=PageResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: UsersService = Depends(get_users_service),
) -> PageResponse[UserResponse]:
    return await service.get_users(page, size)


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: UsersService = Depends(get_users_service),
) -> UserResponse:
    return await service.create_user(data)


@router.get("/users/{user_id}/cart", response_model=CartResponse)
async def get_cart(
    user_id: UUID,
    service: UsersService = Depends(get_users_service),
) -> CartResponse:
    return await service.get_cart(user_id)


@router.post("/users/{user_id}/cart", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart(
    user_id: UUID,
    data: CartCreate,
    service: UsersService = Depends(get_users_service),
) -> CartResponse:
    return await service.create_cart(user_id, data)
