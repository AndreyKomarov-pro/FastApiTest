from http import HTTPStatus
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture
def user_payload():
    return {
        "body": {
            "username": "routeruser",
            "email": "router@test.com",
            "full_name": "Router User",
            "profile": {
                "phone": "+79991234567",
                "address": "Test Address",
                "bio": "Test bio",
            },
        }
    }


async def test_create_user(client: AsyncClient, user_payload):
    response = await client.post("/api/v1/users/", json=user_payload)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["username"] == "routeruser"
    assert data["profile"]["phone"] == "+79991234567"


async def test_list_users(client: AsyncClient, user_payload):
    await client.post("/api/v1/users/", json=user_payload)
    response = await client.get("/api/v1/users/")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "items" in data
    assert data["page"] == 1


async def test_update_user(client: AsyncClient, user_payload):
    create_resp = await client.post("/api/v1/users/", json=user_payload)
    user_id = create_resp.json()["id"]
    update_payload = {"body": {"username": "updatedrouter"}}
    response = await client.put(f"/api/v1/users/{user_id}", json=update_payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["username"] == "updatedrouter"


async def test_delete_user(client: AsyncClient, user_payload):
    create_resp = await client.post("/api/v1/users/", json=user_payload)
    user_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT


async def test_delete_user_not_found(client: AsyncClient):
    response = await client.delete(f"/api/v1/users/{uuid4()}")
    assert response.status_code == HTTPStatus.NOT_FOUND
