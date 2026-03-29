import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException, AlreadyExistsException
from src.models import UserModel, CartModel
from src.repositories.user_repository import UserRepository
from src.repositories.cart_repository import CartRepository
from src.repositories.product_repository import ProductRepository
from src.schemas.users_schemas import UserCreate, UserUpdate, CartCreate

logger = logging.getLogger(__name__)


class UsersService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)
        self.cart_repo = CartRepository(session)
        self.product_repo = ProductRepository(session)

    @staticmethod
    def _to_user_model(data: UserCreate) -> UserModel:
        return UserModel(username=data.username)

    @staticmethod
    def _to_cart_model(data: CartCreate) -> CartModel:
        return CartModel(user_id=data.user_id)

    async def create_user(self, data: UserCreate) -> UserModel:
        logger.info("Creating user username=%s", data.username)
        user = self._to_user_model(data)
        return await self.user_repo.create(user)

    async def get_user_by_id(self, user_id: UUID) -> UserModel:
        logger.debug("Fetching user id=%s", user_id)
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserModel:
        logger.info("Updating user id=%s", user_id)
        user = await self.get_user_by_id(user_id)
        if data.username is not None:
            user.username = data.username
        return await self.user_repo.update(user)

    async def delete_user(self, user_id: UUID) -> None:
        logger.info("Deleting user id=%s", user_id)
        user = await self.get_user_by_id(user_id)
        await self.user_repo.delete(user)

    async def create_cart(self, data: CartCreate) -> CartModel:
        logger.info("Creating cart for user_id=%s", data.user_id)
        user = await self.get_user_by_id(data.user_id)
        existing = await self.cart_repo.get_by_user_id(data.user_id)
        if existing:
            raise AlreadyExistsException("Cart", f"user_id={data.user_id} already has a cart")
        cart = self._to_cart_model(data)
        cart = await self.cart_repo.create(cart)

        for product_id in data.product_ids:
            product = await self.product_repo.get_by_id(product_id)
            if not product:
                raise NotFoundException("Product", product_id)
            await self.cart_repo.add_product(cart.id, product_id)

        return await self.cart_repo.get_by_id(cart.id)

    async def get_cart_by_id(self, cart_id: UUID) -> CartModel:
        logger.debug("Fetching cart id=%s", cart_id)
        cart = await self.cart_repo.get_by_id(cart_id)
        if not cart:
            raise NotFoundException("Cart", cart_id)
        return cart

    async def delete_cart(self, cart_id: UUID) -> None:
        logger.info("Deleting cart id=%s", cart_id)
        cart = await self.get_cart_by_id(cart_id)
        await self.cart_repo.delete(cart)
