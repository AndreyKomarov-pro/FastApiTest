from uuid import UUID
from src.models import UserModel
from src.schemas.user import UserCreate, UserUpdate
from src.exceptions import NotFoundException
from src.router.user.repository import UserRepository
from src.database import get_session


class UserService:
    def __init__(self):
        self._session = None
        self.repo = None

    async def __aenter__(self):
        self._ctx = get_session()
        self._session = await self._ctx.__aenter__()
        self.repo = UserRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def create(self, data: UserCreate) -> UserModel:
        return await self.repo.create(username=data.username)

    async def get(self, user_id: UUID) -> UserModel:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def update(self, user_id: UUID, data: UserUpdate) -> UserModel:
        user = await self.get(user_id)
        return await self.repo.update(user=user, username=data.username)

    async def delete(self, user_id: UUID) -> None:
        user = await self.get(user_id)
        await self.repo.delete(user)
