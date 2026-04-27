import logging
from uuid import UUID

from src.exceptions import NotFoundException
from src.models import UserModel
from src.repositories.user_repository import UserRepository
from src.schemas.pagination import PageResponse
from src.schemas.users import UserCreate, UserUpdate, UserResponse

logger = logging.getLogger(__name__)


class UsersService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def get_users(self, page: int, size: int) -> PageResponse[UserResponse]:
        logger.debug("Listing users page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        return PageResponse.build(
            items=[UserResponse.model_validate(u) for u in items],
            page=page,
            size=size,
        )

    async def create_user(self, data: UserCreate) -> UserResponse:
        logger.info("Creating user username=%s", data.body.username)
        user = UserModel(username=data.body.username)
        result = await self.repo.create(user)
        return UserResponse.model_validate(result)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        logger.info("Updating user id=%s", user_id)
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        for field, value in data.body.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        updated = await self.repo.update(user)
        return UserResponse.model_validate(updated)

    async def delete_user(self, user_id: UUID) -> None:
        logger.info("Deleting user id=%s", user_id)
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        await self.repo.delete(user)
