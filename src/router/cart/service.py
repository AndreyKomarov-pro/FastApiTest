from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import CartModel, UserModel
from src.schemas.cart import CartCreate
from src.exceptions import NotFoundException, AlreadyExistsException
from src.router.cart.repository import CartRepository
from src.router.user.repository import UserRepository


class CartService:
    def __init__(self, session: AsyncSession):
        self.repo = CartRepository(session)
        self.user_repo = UserRepository(session)

    async def create(self, data: CartCreate) -> CartModel:
        user = UserModel(username=data.user.username)
        self.user_repo.session.add(user)
        await self.user_repo.session.flush()

        existing = await self.repo.get_by_user_id(user.id)
        if existing:
            raise AlreadyExistsException("Cart", f"User id={user.id} already has a cart")

        cart = await self.repo.create(user_id=user.id)
        return await self.repo.get_by_id(cart.id)

    async def get(self, cart_id: UUID) -> CartModel:
        cart = await self.repo.get_by_id(cart_id)
        if not cart:
            raise NotFoundException("Cart", cart_id)
        return cart

    async def delete(self, cart_id: UUID) -> None:
        cart = await self.repo.get_by_id(cart_id)
        if not cart:
            raise NotFoundException("Cart", cart_id)
        await self.repo.delete(cart)

