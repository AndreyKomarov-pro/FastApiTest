from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import UserModel, CartModel, ProductModel, cart_products


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        return await self.session.get(UserModel, user_id)

    async def get_with_cart(self, user_id: UUID) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(selectinload(UserModel.cart).selectinload(CartModel.products))
        )
        return result.scalar_one_or_none()

    async def get_product(self, product_id: UUID) -> ProductModel | None:
        return await self.session.get(ProductModel, product_id)

    async def create_cart(self, cart: CartModel) -> CartModel:
        self.session.add(cart)
        await self.session.flush()
        return cart

    async def delete_cart(self, cart: CartModel) -> None:
        await self.session.delete(cart)

    async def add_product_to_cart(self, cart_id: UUID, product_id: UUID) -> None:
        await self.session.execute(
            cart_products.insert().values(cart_id=cart_id, product_id=product_id)
        )

    async def get_cart_by_id(self, cart_id: UUID) -> CartModel | None:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.id == cart_id)
            .options(
                selectinload(CartModel.user),
                selectinload(CartModel.products),
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int, offset: int) -> list[UserModel]:
        result = await self.session.execute(
            select(UserModel).order_by(UserModel.created_at.desc()).limit(limit).offset(offset).with_for_update(skip_locked=True)
        )
        return list(result.scalars().all())

    async def create(self, user: UserModel) -> UserModel:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: UserModel) -> UserModel:
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: UserModel) -> None:
        await self.session.delete(user)
