import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.enums.order_status import OrderStatus
from src.exceptions import NotFoundException
from src.models import OrderModel, OrderEntry, ProductModel
from src.repositories.order_repository import OrderRepository
from src.repositories.order_item_repository import OrderItemRepository
from src.repositories.product_repository import ProductRepository
from src.schemas.orders import OrderCreate, OrderUpdate, OrderResponse, OrderItemCreate, OrderItemResponse
from src.schemas.pagination import PageResponse

logger = logging.getLogger(__name__)


class OrdersService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.order_repo = OrderRepository(session)
        self.item_repo = OrderItemRepository(session)
        self.product_repo = ProductRepository(session)

    @staticmethod
    def _to_order_model(data: OrderCreate) -> OrderModel:
        return OrderModel(user_id=data.user_id, status=OrderStatus.PENDING, total_amount=0)

    @staticmethod
    def _to_order_item_model(order_id: UUID, product: ProductModel, data: OrderItemCreate) -> OrderEntry:
        return OrderEntry(
            order_id=order_id,
            product_id=product.id,
            quantity=data.quantity,
            price=Decimal(str(product.price)),
        )

    async def _fetch_order(self, order_id: UUID) -> OrderModel:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        return order

    async def _fetch_product(self, product_id: UUID) -> ProductModel:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product

    async def create_order(self, data: OrderCreate) -> OrderResponse:
        logger.info("Creating order for user_id=%s", data.user_id)
        order = self._to_order_model(data)
        order = await self.order_repo.create(order)

        total = await self._add_items_to_order(order.id, data.item_ids)
        await self.order_repo.update_total(order, total)

        result = await self.order_repo.get_by_id(order.id)
        return OrderResponse.model_validate(result)

    async def get_order_by_id(self, order_id: UUID) -> OrderResponse:
        logger.debug("Fetching order id=%s", order_id)
        order = await self._fetch_order(order_id)
        return OrderResponse.model_validate(order)

    async def update_order(self, order_id: UUID, data: OrderUpdate) -> OrderResponse:
        logger.info("Updating order id=%s", order_id)
        order = await self._fetch_order(order_id)
        if data.status is not None:
            order.status = data.status
            await self.order_repo.update(order)
        result = await self.order_repo.get_by_id(order_id)
        return OrderResponse.model_validate(result)

    async def get_orders(self, page: int, size: int) -> PageResponse[OrderResponse]:
        logger.debug("Listing orders page=%s size=%s", page, size)
        offset = (page - 1) * size
        items = await self.order_repo.get_all(size, offset)
        return PageResponse.build(
            items=[OrderResponse.model_validate(o) for o in items],
            page=page,
            size=size,
        )

    async def get_order_items(self, order_id: UUID) -> list[OrderItemResponse]:
        logger.debug("Listing items for order_id=%s", order_id)
        await self._fetch_order(order_id)
        items = await self.item_repo.get_by_order_id(order_id)
        return [OrderItemResponse.model_validate(i) for i in items]

    async def add_item_to_order(self, order_id: UUID, data: OrderItemCreate) -> OrderItemResponse:
        logger.info("Adding item to order_id=%s product_id=%s", order_id, data.product_id)
        await self._fetch_order(order_id)
        product = await self._fetch_product(data.product_id)
        item = self._to_order_item_model(order_id, product, data)
        item = await self.item_repo.create(item)
        item.product = product
        await self.item_repo.recalc_order_total(order_id)
        return OrderItemResponse.model_validate(item)

    async def delete_order(self, order_id: UUID) -> None:
        logger.info("Deleting order id=%s", order_id)
        order = await self._fetch_order(order_id)
        await self.order_repo.delete(order)

    async def _add_items_to_order(
        self, order_id: UUID, items_data: list[OrderItemCreate]
    ) -> Decimal:
        total = Decimal("0")
        for item_data in items_data:
            product = await self._fetch_product(item_data.product_id)
            item = self._to_order_item_model(order_id, product, item_data)
            await self.item_repo.create(item)
            total += Decimal(str(product.price)) * item_data.quantity
        return total
