from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.user_repository import UserRepository
from src.schemas.pagination import PageResponse
from src.schemas.users import UserCreate, UserUpdate, UserResponse
from src.services.users_service import UsersService

router = APIRouter(tags=["Users"])


@router.get("/users/", response_model=PageResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> PageResponse[UserResponse]:
    service = UsersService(UserRepository(session))
    return await service.get_users(page, size)


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UsersService(UserRepository(session))
    return await service.create_user(data)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UsersService(UserRepository(session))
    return await service.update_user(user_id, data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    service = UsersService(UserRepository(session))
    await service.delete_user(user_id)
