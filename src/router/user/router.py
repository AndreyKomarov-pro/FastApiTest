from fastapi import APIRouter, status
from uuid import UUID

from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.router.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate):
    async with UserService() as service:
        user = await service.create(data)
        return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    async with UserService() as service:
        user = await service.get(user_id)
        return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, data: UserUpdate):
    async with UserService() as service:
        user = await service.update(user_id, data)
        return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID):
    async with UserService() as service:
        await service.delete(user_id)
