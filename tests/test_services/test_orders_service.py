from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.cache_service import CacheService
from src.enums.order_status import OrderStatus
from src.exceptions import NotFoundException
from src.models.user import UserModel
from src.models.user_profile import UserProfile
from src.models.category import CategoryModel
from src.models.product import ProductModel
from src.repositories.orders_repository import OrdersRepository
from src.schemas.order import (
    OrderCreate,
    OrderBody,
    OrderEntryBody,
    OrderUpdate,
    OrderUpdateBody,
)
from src.services.orders_service import OrdersService


@pytest.fixture
def orders_service(session, cache_service):
    repo = OrdersRepository(session)
    return OrdersService(repo, cache_service)


@pytest.fixture
async def test_user(session):
    user = UserModel(username="orderuser", email="order@test.com", full_name="Order User")
    user.profile = UserProfile(phone="+79991111111")
    session.add(user)
    await session.flush()
    return user


@pytest.fixture
async def test_product(session):
    category = CategoryModel(name="Order Category", description="For orders")
    session.add(category)
    await session.flush()
    product = ProductModel(
        name="Order Product",
        description="For orders",
        price=Decimal("50.00"),
        quantity=100,
        category_id=category.id,
    )
    session.add(product)
    await session.flush()
    return product


@pytest.fixture
def order_data(test_user, test_product):
    return OrderCreate(
        body=OrderBody(
            user_id=test_user.id,
            items=[
                OrderEntryBody(
                    product_id=test_product.id,
                    quantity=2,
                    price=Decimal("50.00"),
                )
            ],
        )
    )


async def test_create_order(orders_service, order_data):
    result = await orders_service.create_order(order_data)
    assert result.status == OrderStatus.PENDING
    assert len(result.order_entries) == 1
    assert result.order_entries[0].quantity == 2


async def test_get_orders(orders_service, order_data):
    await orders_service.create_order(order_data)
    result = await orders_service.get_orders(page=1, size=10)
    assert result.page == 1
    assert len(result.items) >= 1


async def test_update_order_status(orders_service, order_data):
    created = await orders_service.create_order(order_data)
    update_data = OrderUpdate(body=OrderUpdateBody(status=OrderStatus.PAID))
    result = await orders_service.update_order(created.id, update_data)
    assert result.status == OrderStatus.PAID


async def test_delete_order(orders_service, order_data):
    created = await orders_service.create_order(order_data)
    await orders_service.delete_order(created.id)
    with pytest.raises(NotFoundException):
        await orders_service._get_order_orm(created.id)


async def test_get_order_not_found(orders_service):
    with pytest.raises(NotFoundException):
        await orders_service._get_order_orm(uuid4())
