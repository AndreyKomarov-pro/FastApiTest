from http import HTTPStatus
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture
def category_payload():
    return {
        "body": {
            "name": "Router Category",
            "description": "Router test",
            "products": [
                {
                    "name": "Router Product",
                    "description": "Product",
                    "price": "19.99",
                    "quantity": 5,
                }
            ],
        }
    }


async def test_create_category(client: AsyncClient, category_payload, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    response = await client.post("/api/v1/categories/", json=category_payload)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["name"] == "Router Category"
    assert len(data["products"]) == 1


async def test_list_categories(client: AsyncClient, category_payload, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    await client.post("/api/v1/categories/", json=category_payload)
    response = await client.get("/api/v1/categories/")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "items" in data
    assert data["page"] == 1


async def test_get_category_by_id(client: AsyncClient, category_payload, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    mock_product_info_client.get_product_info.return_value = None
    create_resp = await client.post("/api/v1/categories/", json=category_payload)
    category_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == category_id


async def test_get_category_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/categories/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_update_category(client: AsyncClient, category_payload, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    mock_product_info_client.get_product_info.return_value = None
    create_resp = await client.post("/api/v1/categories/", json=category_payload)
    category_id = create_resp.json()["id"]
    update_payload = {"body": {"name": "Updated", "description": "Updated desc"}}
    response = await client.put(f"/api/v1/categories/{category_id}", json=update_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "Updated"


async def test_delete_category(client: AsyncClient, category_payload, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    create_resp = await client.post("/api/v1/categories/", json=category_payload)
    category_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/categories/{category_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT
