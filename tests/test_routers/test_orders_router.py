from decimal import Decimal
from http import HTTPStatus
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import UserModel
from src.models.user_profile import UserProfile
from src.models.category import CategoryModel
from src.models.product import ProductModel


@pytest.fixture
async def order_prerequisites(session: AsyncSession):
    user = UserModel(username="orderrouteruser", email="orderrouter@test.com", full_name="Order Router")
    user.profile = UserProfile(phone="+79992222222")
    session.add(user)
    await session.flush()

    category = CategoryModel(name="Order Router Cat", description="For router tests")
    session.add(category)
    await session.flush()

    product = ProductModel(
        name="Order Router Product",
        price=Decimal("25.00"),
        quantity=50,
        category_id=category.id,
    )
    session.add(product)
    await session.flush()

    return user, product


@pytest.fixture
def order_payload(order_prerequisites):
    user, product = order_prerequisites
    return {
        "body": {
            "user_id": str(user.id),
            "items": [
                {
                    "product_id": str(product.id),
                    "quantity": 3,
                    "price": "25.00",
                }
            ],
        }
    }


async def test_create_order(client: AsyncClient, order_payload):
    response = await client.post("/api/v1/orders/", json=order_payload)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["status"] == "PENDING"
    assert len(data["order_entries"]) == 1


async def test_list_orders(client: AsyncClient, order_payload):
    await client.post("/api/v1/orders/", json=order_payload)
    response = await client.get("/api/v1/orders/")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "items" in data


async def test_update_order(client: AsyncClient, order_payload):
    create_resp = await client.post("/api/v1/orders/", json=order_payload)
    order_id = create_resp.json()["id"]
    update_payload = {"body": {"status": "PAID"}}
    response = await client.put(f"/api/v1/orders/{order_id}", json=update_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "PAID"


async def test_delete_order(client: AsyncClient, order_payload):
    create_resp = await client.post("/api/v1/orders/", json=order_payload)
    order_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/orders/{order_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT


async def test_delete_order_not_found(client: AsyncClient):
    response = await client.delete(f"/api/v1/orders/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND
