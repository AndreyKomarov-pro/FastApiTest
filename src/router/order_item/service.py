from uuid import UUID
from src.models import OrderItemModel, ProductModel, CategoryModel
from src.schemas.order_item import OrderItemCreate, OrderItemUpdate
from src.exceptions import NotFoundException
from src.router.order_item.repository import OrderItemRepository
from src.database import get_session


class OrderItemService:
    def __init__(self):
        self._session = None
        self.repo = None

    async def __aenter__(self):
        self._ctx = get_session()
        self._session = await self._ctx.__aenter__()
        self.repo = OrderItemRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._ctx.__aexit__(exc_type, exc_val, exc_tb)

    async def create(self, order_id: UUID, data: OrderItemCreate) -> OrderItemModel:
        order = await self.repo.get_order(order_id)
        if not order:
            raise NotFoundException("Order", order_id)

        category = CategoryModel(
            name=data.product.category.name,
            description=data.product.category.description,
        )
        self._session.add(category)
        await self._session.flush()

        product = ProductModel(
            name=data.product.name,
            description=data.product.description,
            price=data.product.price,
            quantity=data.product.quantity,
            category_id=category.id,
        )
        self._session.add(product)
        await self._session.flush()

        item = await self.repo.create(
            order_id=order_id,
            product_id=product.id,
            quantity=data.quantity,
            price=float(product.price),
        )
        await self.repo.recalc_order_total(order_id)
        return await self.repo.get_by_id(item.id)

    async def get(self, item_id: UUID) -> OrderItemModel:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("OrderItem", item_id)
        return item

    async def update(self, item_id: UUID, data: OrderItemUpdate) -> OrderItemModel:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("OrderItem", item_id)
        await self.repo.update(item, quantity=data.quantity)
        await self.repo.recalc_order_total(item.order_id)
        return await self.repo.get_by_id(item_id)

    async def delete(self, item_id: UUID) -> None:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise NotFoundException("OrderItem", item_id)
        order_id = item.order_id
        await self.repo.delete(item)
        await self.repo.recalc_order_total(order_id)
