from decimal import Decimal
from uuid import uuid4

import pytest

from src.exceptions import NotFoundException
from src.repositories.category_repository import CategoryRepository
from src.schemas.catalog import CategoryCreate, CategoryBody, CategoryUpdate, CategoryUpdateBody, ProductBody
from src.services.category_service import CategoryService


@pytest.fixture
def category_service(session, cache_service, mock_product_info_client):
    repo = CategoryRepository(session)
    return CategoryService(repo, cache_service, mock_product_info_client)


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


async def test_create_category(category_service, category_data, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    result = await category_service.create_category(category_data)
    assert result.name == "Test Category"
    assert result.description == "Test description"
    assert len(result.products) == 1
    assert result.products[0].name == "Test Product"


async def test_get_categories(category_service, category_data, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    await category_service.create_category(category_data)
    result = await category_service.get_categories(page=1, size=10)
    assert result.page == 1
    assert len(result.items) >= 1


async def test_get_category_by_id(category_service, category_data, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    mock_product_info_client.get_product_info.return_value = None
    created = await category_service.create_category(category_data)
    result = await category_service.get_category_by_id(created.id)
    assert result.id == created.id
    assert result.name == "Test Category"


async def test_get_category_not_found(category_service):
    with pytest.raises(NotFoundException):
        await category_service.get_category_by_id(uuid4())


async def test_update_category(category_service, category_data, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    created = await category_service.create_category(category_data)
    update_data = CategoryUpdate(
        body=CategoryUpdateBody(name="Updated Name", description="Updated desc")
    )
    result = await category_service.update_category(created.id, update_data)
    assert result.name == "Updated Name"
    assert result.description == "Updated desc"


async def test_delete_category(category_service, category_data, mock_product_info_client):
    mock_product_info_client.create_product_info.return_value = None
    created = await category_service.create_category(category_data)
    await category_service.delete_category(created.id)
    with pytest.raises(NotFoundException):
        await category_service.get_category_by_id(created.id)
