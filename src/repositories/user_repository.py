from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.user import UserModel

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int, offset: int) -> list[UserModel]:
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.profile))
            .where(UserModel.is_deleted == False)
            .order_by(UserModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.profile))
            .where(UserModel.id == user_id, UserModel.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_by_id_for_update(self, user_id: UUID) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.profile))
            .where(UserModel.id == user_id, UserModel.is_deleted == False)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def create(self, user: UserModel) -> UserModel:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user, attribute_names=["profile"])
        return user

    async def update(self, user: UserModel) -> UserModel:
        await self.session.flush()
        await self.session.refresh(user, attribute_names=["profile"])
        return user

    async def delete(self, user: UserModel) -> None:
        user.is_deleted = True
        await self.session.flush()
