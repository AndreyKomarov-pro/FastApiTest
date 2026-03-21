from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException, AlreadyExistsException
from src.models import UserModel, CartModel
from src.router.users.repository import UserRepository, CartRepository
from src.router.users.schemas import UserCreate, UserUpdate, CartCreate


class UsersService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)
        self.cart_repo = CartRepository(session)

    # ── User ──────────────────────────────────────────────────────────────────

    async def create_user(self, data: UserCreate) -> UserModel:
        return await self.user_repo.create(data)

    async def get_user_by_id(self, user_id: UUID) -> UserModel:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserModel:
        user = await self.get_user_by_id(user_id)
        return await self.user_repo.update(user, data)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.get_user_by_id(user_id)
        await self.user_repo.delete(user)

    # ── Cart ──────────────────────────────────────────────────────────────────

    async def create_cart(self, data: CartCreate) -> CartModel:
        # Verify the user exists
        await self.get_user_by_id(data.user_id)

        # Check by the unique FK — a user can have only one cart
        existing = await self.cart_repo.get_by_user_id(data.user_id)
        if existing:
            raise AlreadyExistsException("Cart", f"user_id={data.user_id} already has a cart")

        cart = await self.cart_repo.create(user_id=data.user_id)
        return await self.cart_repo.get_by_id(cart.id)

    async def get_cart_by_id(self, cart_id: UUID) -> CartModel:
        cart = await self.cart_repo.get_by_id(cart_id)
        if not cart:
            raise NotFoundException("Cart", cart_id)
        return cart

    async def delete_cart(self, cart_id: UUID) -> None:
        cart = await self.get_cart_by_id(cart_id)
        await self.cart_repo.delete(cart)
