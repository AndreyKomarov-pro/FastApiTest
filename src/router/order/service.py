from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import OrderModel, UserModel, ProductModel, OrderItemModel, CategoryModel
from src.schemas.order import OrderCreate, OrderUpdate
from src.exceptions import NotFoundException
from src.router.order.repository import OrderRepository


class OrderService:
    def __init__(self, session: AsyncSession):
        self.repo = OrderRepository(session)
        self.session = session

    async def create(self, data: OrderCreate) -> OrderModel:
        user = UserModel(username=data.user.username)
        self.session.add(user)
        await self.session.flush()

        order = await self.repo.create(user_id=user.id)
        total = 0.0

        for item_data in data.items:
            category = CategoryModel(
                name=item_data.product.category.name,
                description=item_data.product.category.description,
            )
            self.session.add(category)
            await self.session.flush()

            product = ProductModel(
                name=item_data.product.name,
                description=item_data.product.description,
                price=item_data.product.price,
                quantity=item_data.product.quantity,
                category_id=category.id,
            )
            self.session.add(product)
            await self.session.flush()

            item = OrderItemModel(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data.quantity,
                price=product.price,
            )
            self.session.add(item)
            total += product.price * item_data.quantity

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
