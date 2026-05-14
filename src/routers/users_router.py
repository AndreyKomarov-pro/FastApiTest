from uuid import UUID
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from src.dependencies import get_users_service
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.schemas.pagination import PageResponse
from src.services.users_service import UsersService

router = APIRouter(tags=["Users"])

@router.get("/users/", response_model=PageResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: UsersService = Depends(get_users_service),
) -> PageResponse[UserResponse]:
    return await service.get_users(page, size)

@router.post("/users/", response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def create_user(
    data: UserCreate,
    service: UsersService = Depends(get_users_service),
) -> UserResponse:
    return await service.create_user(data)

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UsersService = Depends(get_users_service),
) -> UserResponse:
    return await service.update_user(user_id, data)

@router.delete("/users/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: UsersService = Depends(get_users_service),
) -> None:
    await service.delete_user(user_id)
