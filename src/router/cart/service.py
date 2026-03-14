from uuid import UUID
from src.models import CartModel, UserModel
from src.schemas.cart import CartCreate
from src.exceptions import NotFoundException, AlreadyExistsException
from src.router.cart.repository import CartRepository
from src.router.user.repository import UserRepository
from src.database import get_session


class CartService:
    def __init__(self):
        self._session = None
        self.repo = None
        self.user_repo = None

    async def __aenter__(self):
        self._ctx = get_session()
        self._session = await self._ctx.__aenter__()
        self.repo = CartRepository(self._session)
        self.user_repo = UserRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def create(self, data: CartCreate) -> CartModel:
        user = UserModel(username=data.user.username)
        self._session.add(user)
        await self._session.flush()

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
