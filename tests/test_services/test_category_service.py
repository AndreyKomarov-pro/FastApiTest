from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.enums.category_status import CategoryStatus
from src.exceptions import NotFoundException
from src.repositories.category_repository import CategoryRepository
from src.schemas.catalog import CategoryCreate, CategoryBody, CategoryUpdate, CategoryUpdateBody, ProductBody
from src.schemas.product_info import ProductInfoResponse
from src.services.category_service import CategoryService


@pytest.fixture
def category_service(session, cache_service, mock_product_info_client):
    repo = CategoryRepository(session)
    return CategoryService(repo, cache_service, mock_product_info_client)


@pytest.fixture
def product_info_response():
    return ProductInfoResponse(
        id=uuid4(),
        product_id=uuid4(),
        rating=Decimal("0"),
        reviews_count=0,
        warehouse_stock=10,
    )


@pytest.fixture
def category_data():
    return CategoryCreate(
        body=CategoryBody(
            name="Test Category",
            description="Test description",
            products=[
                ProductBody(
                    name="Test Product",
                    description="Product desc",
                    price=Decimal("99.99"),
                    quantity=10,
                )
            ],
        )
    )


async def test_create_category_pending(category_service, category_data):
    result = await category_service.create_category(category_data)
    assert result.name == "Test Category"
    assert result.status == CategoryStatus.PENDING
    assert len(result.products) == 1


async def test_get_categories(category_service, category_data):
    await category_service.create_category(category_data)
    result = await category_service.get_categories(page=1, size=10)
    assert result.page == 1
    assert len(result.items) >= 1


async def test_get_category_by_id(category_service, category_data, mock_product_info_client, product_info_response):
    mock_product_info_client.get_product_info.return_value = product_info_response
    created = await category_service.create_category(category_data)
    result = await category_service.get_category_by_id(created.id)
    assert result.id == created.id
    assert result.name == "Test Category"


async def test_get_category_not_found(category_service):
    with pytest.raises(NotFoundException):
        await category_service.get_category_by_id(uuid4())


async def test_update_category(category_service, category_data, mock_product_info_client, product_info_response):
    mock_product_info_client.get_product_info.return_value = product_info_response
    created = await category_service.create_category(category_data)
    update_data = CategoryUpdate(
        body=CategoryUpdateBody(name="Updated Name", description="Updated desc")
    )
    result = await category_service.update_category(created.id, update_data)
    assert result.name == "Updated Name"
    assert result.description == "Updated desc"


async def test_delete_category(category_service, category_data, mock_product_info_client, product_info_response):
    mock_product_info_client.get_product_info.return_value = product_info_response
    created = await category_service.create_category(category_data)
    await category_service.delete_category(created.id)
    with pytest.raises(NotFoundException):
        await category_service.get_category_by_id(created.id)


async def test_get_category_by_id_returns_cached(category_service, category_data, mock_product_info_client, product_info_response):
    mock_product_info_client.get_product_info.return_value = product_info_response
    created = await category_service.create_category(category_data)
    await category_service.get_category_by_id(created.id)
    await category_service.get_category_by_id(created.id)
    mock_product_info_client.get_product_info.assert_called_once()


async def test_update_sets_cache(category_service, category_data, mock_product_info_client, product_info_response):
    mock_product_info_client.get_product_info.return_value = product_info_response
    created = await category_service.create_category(category_data)
    await category_service.get_category_by_id(created.id)
    mock_product_info_client.get_product_info.reset_mock()
    result = await category_service.update_category(
        created.id, CategoryUpdate(body=CategoryUpdateBody(name="New Name"))
    )
    assert result.name == "New Name"
    cached_result = await category_service.get_category_by_id(created.id)
    assert cached_result.name == "New Name"
    mock_product_info_client.get_product_info.assert_not_called()
