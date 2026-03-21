from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import UserModel, CartModel, ProductModel
from src.router.users.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        return await self.session.get(UserModel, user_id)

    async def create(self, data: UserCreate) -> UserModel:
        user = UserModel(username=data.username)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: UserModel, data: UserUpdate) -> UserModel:
        if data.username is not None:
            user.username = data.username
        await self.session.flush()
        return user

    async def delete(self, user: UserModel) -> None:
        await self.session.delete(user)


class CartRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, cart_id: UUID) -> CartModel | None:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.id == cart_id)
            .options(
                selectinload(CartModel.user),
                selectinload(CartModel.products).selectinload(ProductModel.category),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> CartModel | None:
        result = await self.session.execute(
            select(CartModel).where(CartModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: UUID) -> CartModel:
        cart = CartModel(user_id=user_id)
        self.session.add(cart)
        await self.session.flush()
        return cart

    async def delete(self, cart: CartModel) -> None:
        await self.session.delete(cart)
