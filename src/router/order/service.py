from uuid import UUID
from src.models import OrderModel, UserModel, ProductModel, OrderItemModel, CategoryModel
from src.schemas.order import OrderCreate, OrderUpdate
from src.exceptions import NotFoundException
from src.router.order.repository import OrderRepository
from src.database import get_session


class OrderService:
    def __init__(self):
        self._session = None
        self.repo = None

    async def __aenter__(self):
        self._ctx = get_session()
        self._session = await self._ctx.__aenter__()
        self.repo = OrderRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def create(self, data: OrderCreate) -> OrderModel:
        user = UserModel(username=data.user.username)
        self._session.add(user)
        await self._session.flush()

        order = await self.repo.create(user_id=user.id)
        total = 0.0

        for item_data in data.items:
            category = CategoryModel(
                name=item_data.product.category.name,
                description=item_data.product.category.description,
            )
            self._session.add(category)
            await self._session.flush()

            product = ProductModel(
                name=item_data.product.name,
                description=item_data.product.description,
                price=item_data.product.price,
                quantity=item_data.product.quantity,
                category_id=category.id,
            )
            self._session.add(product)
            await self._session.flush()

            item = OrderItemModel(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data.quantity,
                price=product.price,
            )
            self._session.add(item)
            total += float(product.price) * item_data.quantity

        await self.repo.update_total(order, total)
        return await self.repo.get_by_id(order.id)

    async def get(self, order_id: UUID) -> OrderModel:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return order

    async def update(self, order_id: UUID, data: OrderUpdate) -> OrderModel:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        if data.status is not None:
            await self.repo.update_status(order, data.status)
        return await self.repo.get_by_id(order_id)

    async def delete(self, order_id: UUID) -> None:
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        await self.repo.delete(order)
