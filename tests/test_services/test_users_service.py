from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.cache_service import CacheService
from src.exceptions import NotFoundException
from src.repositories.user_repository import UserRepository
from src.schemas.user import (
    UserCreate,
    UserBody,
    UserProfileBody,
    UserUpdate,
    UserUpdateBody,
    UserProfileUpdateBody,
)
from src.services.users_service import UsersService


@pytest.fixture
def users_service(session, cache_service):
    repo = UserRepository(session)
    return UsersService(repo, cache_service)


@pytest.fixture
def user_data():
    return UserCreate(
        body=UserBody(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            profile=UserProfileBody(
                phone="+79991234567",
                address="Moscow, Russia",
                bio="Test bio",
            ),
        )
    )


async def test_create_user(users_service, user_data):
    result = await users_service.create_user(user_data)
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.profile is not None
    assert result.profile.phone == "+79991234567"


async def test_get_users(users_service, user_data):
    await users_service.create_user(user_data)
    result = await users_service.get_users(page=1, size=10)
    assert result.page == 1
    assert len(result.items) >= 1


async def test_update_user(users_service, user_data):
    created = await users_service.create_user(user_data)
    update_data = UserUpdate(
        body=UserUpdateBody(
            username="updateduser",
            profile=UserProfileUpdateBody(phone="+79990000000"),
        )
    )
    result = await users_service.update_user(created.id, update_data)
    assert result.username == "updateduser"
    assert result.profile.phone == "+79990000000"


async def test_delete_user(users_service, user_data):
    created = await users_service.create_user(user_data)
    await users_service.delete_user(created.id)
    with pytest.raises(NotFoundException):
        await users_service._get_user_orm(created.id)


async def test_get_user_not_found(users_service):
    with pytest.raises(NotFoundException):
        await users_service._get_user_orm(uuid4())
