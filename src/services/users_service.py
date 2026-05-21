import logging
from uuid import UUID
from src.exceptions import NotFoundException
from src.models.user import UserModel
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)

class UsersService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def _get_user_orm(self, user_id: UUID) -> UserModel:
        user = await self.repo.get_by_id_for_update(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def get_users(self, page: int, size: int) -> PageResponse[UserResponse]:
        logger.debug("Listing users page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        return PageResponse(
            items=UserResponse.from_list(items),
            page=page,
            size=size,
        )

    async def create_user(self, data: UserCreate) -> UserResponse:
        logger.info("Creating user username=%s", data.body.username)
        user = data.body.to_model()
        result = await self.repo.create(user)
        return UserResponse.from_model(result)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        logger.info("Updating user id=%s", user_id)
        user = await self._get_user_orm(user_id)
        data.body.apply_to(user)
        result = await self.repo.update(user)
        return UserResponse.from_model(result)

    async def delete_user(self, user_id: UUID) -> None:
        logger.info("Deleting user id=%s", user_id)
        user = await self._get_user_orm(user_id)
        await self.repo.delete(user)
