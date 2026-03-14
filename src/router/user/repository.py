from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        return await self.session.get(UserModel, user_id)

    async def create(self, username: str) -> UserModel:
        user = UserModel(username=username)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: UserModel, username: str | None) -> UserModel:
        if username is not None:
            user.username = username
        await self.session.flush()
        return user

    async def delete(self, user: UserModel) -> None:
        await self.session.delete(user)
