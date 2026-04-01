import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundException, AlreadyExistsException
from src.models import UserModel, CartModel
from src.repositories.user_repository import UserRepository
from src.repositories.cart_repository import CartRepository
from src.schemas.pagination import PageResponse
from src.schemas.users_schemas import UserCreate, UserUpdate, UserResponse, CartCreate, CartResponse

logger = logging.getLogger(__name__)


class UsersService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repo = UserRepository(session)
        self.cart_repo = CartRepository(session)

    async def _fetch_user(self, user_id: UUID) -> UserModel:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user

    async def _fetch_cart(self, cart_id: UUID) -> CartModel:
        cart = await self.cart_repo.get_by_id(cart_id)
        if not cart:
            raise NotFoundException("Cart", cart_id)
        return cart

    async def create_user(self, data: UserCreate) -> UserResponse:
        logger.info("Creating user username=%s", data.username)
        user = UserModel(username=data.username)
        result = await self.user_repo.create(user)
        logger.debug("User created id=%s", result.id)
        return UserResponse.model_validate(result)

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        logger.debug("Fetching user id=%s", user_id)
        user = await self._fetch_user(user_id)
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> UserResponse:
        logger.info("Updating user id=%s", user_id)
        user = await self._fetch_user(user_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        updated = await self.user_repo.update(user)
        return UserResponse.model_validate(updated)

    async def delete_user(self, user_id: UUID) -> None:
        logger.info("Deleting user id=%s", user_id)
        user = await self._fetch_user(user_id)
        await self.user_repo.delete(user)

    async def get_users(self, page: int, size: int) -> PageResponse[UserResponse]:
        logger.debug("Listing users page=%s size=%s", page, size)
        offset = (page - 1) * size
        items, total = await self.user_repo.get_all(size, offset), await self.user_repo.count()
        return PageResponse.build(
            items=[UserResponse.model_validate(u) for u in items],
            total=total,
            page=page,
            size=size,
        )

    async def create_cart(self, data: CartCreate) -> CartResponse:
        logger.info("Creating cart for user_id=%s", data.user_id)
        await self._fetch_user(data.user_id)
        existing = await self.cart_repo.get_by_user_id(data.user_id)
        if existing:
            raise AlreadyExistsException("Cart", f"user_id={data.user_id} already has a cart")

        cart = CartModel(user_id=data.user_id)
        cart = await self.cart_repo.create(cart)

        for product_id in data.product_ids:
            product = await self.cart_repo.get_product(product_id)
            if not product:
                raise NotFoundException("Product", product_id)
            await self.cart_repo.add_product(cart.id, product_id)

        result = await self.cart_repo.get_by_id(cart.id)
        return CartResponse.model_validate(result)

    async def get_cart_by_id(self, cart_id: UUID) -> CartResponse:
        logger.debug("Fetching cart id=%s", cart_id)
        cart = await self._fetch_cart(cart_id)
        return CartResponse.model_validate(cart)

    async def delete_cart(self, cart_id: UUID) -> None:
        logger.info("Deleting cart id=%s", cart_id)
        cart = await self._fetch_cart(cart_id)
        await self.cart_repo.delete(cart)
