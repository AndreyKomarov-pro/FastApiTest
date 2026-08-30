import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.cache.redis_client import RedisClient
from src.config import settings
from src.exceptions import NotFoundException
from src.models.enums.event_type import EventType
from src.models.outbox_event import OutboxEventModel
from src.models.user import UserModel
from src.models.user_profile import UserProfile
from src.repositories.outbox_repository import OutboxRepository
from src.repositories.user_repository import UserRepository
from src.schemas.event import EventEnvelope
from src.schemas.user import UserCreate, UserUpdate, UserUpdateBody, UserResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)

USERS_LIST_KEY = "users:page:{page}:size:{size}"
USER_KEY = "user:{user_id}"
AGGREGATE_TYPE = "user"


class UsersService:
    def __init__(
        self,
        repo: UserRepository,
        cache: RedisClient,
        outbox_repo: OutboxRepository,
    ) -> None:
        self.repo = repo
        self.cache = cache
        self.outbox_repo = outbox_repo

    async def _get_user_orm(self, user_id: UUID) -> UserModel:
        user = await self.repo.get_by_id_for_update(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def get_users(self, page: int, size: int) -> PageResponse[UserResponse]:
        logger.debug("Listing users page=%s size=%s", page, size)
        cache_key = USERS_LIST_KEY.format(page=page, size=size)
        cached = await self.cache.get_cached(cache_key)
        if cached:
            return PageResponse[UserResponse].model_validate(cached)
        offset = (page - 1) * size
        items = await self.repo.get_all(size, offset)
        result = PageResponse(
            items=UserResponse.from_list(items),
            page=page,
            size=size,
        )
        await self.cache.set_cached(cache_key, result.model_dump(mode="json"))
        return result

    async def create_user(self, data: UserCreate) -> UserResponse:
        logger.info("Creating user username=%s", data.body.username)
        user = UserModel(
            username=data.body.username,
            email=data.body.email,
            full_name=data.body.full_name,
        )
        user.profile = UserProfile(
            phone=data.body.profile.phone,
            address=data.body.profile.address,
            bio=data.body.profile.bio,
        )
        result = await self.repo.create(user)

        await self._publish_event(
            aggregate_id=result.id,
            data=data.body.model_dump(mode="json"),
        )

        return UserResponse.from_model(result)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        logger.info("Updating user id=%s", user_id)
        user = await self._get_user_orm(user_id)
        self._apply_update(user, data.body)
        result = await self.repo.update(user)
        await self.cache.delete_cached(USER_KEY.format(user_id=user_id))
        return UserResponse.from_model(result)

    @staticmethod
    def _apply_update(user: UserModel, fields: UserUpdateBody) -> None:
        for key, value in fields.model_dump(exclude_unset=True, exclude={"profile"}).items():
            setattr(user, key, value)
        if fields.profile:
            if user.profile:
                for key, value in fields.profile.model_dump(exclude_unset=True).items():
                    setattr(user.profile, key, value)
            else:
                user.profile = UserProfile(
                    phone=fields.profile.phone,
                    address=fields.profile.address,
                    bio=fields.profile.bio,
                )

    async def delete_user(self, user_id: UUID) -> None:
        logger.info("Deleting user id=%s", user_id)
        user = await self._get_user_orm(user_id)
        await self.repo.delete(user)
        await self.cache.delete_cached_pattern("users:*")
        await self.cache.delete_cached(USER_KEY.format(user_id=user_id))

    async def _publish_event(
        self,
        aggregate_id: UUID,
        data: dict,
    ) -> None:
        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type=EventType.CREATED,
            aggregate_type=AGGREGATE_TYPE,
            aggregate_id=aggregate_id,
            timestamp=datetime.now(timezone.utc),
            data=data,
        )
        outbox_event = OutboxEventModel(
            aggregate_type=AGGREGATE_TYPE,
            aggregate_id=aggregate_id,
            event_type=EventType.CREATED,
            topic=settings.kafka_topic_users,
            payload=envelope.model_dump_json(),
        )
        await self.outbox_repo.create(outbox_event)
