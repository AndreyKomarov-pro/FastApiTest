from decimal import Decimal

import pytest

from src.exceptions.validation import ValidationException
from src.schemas.catalog import ProductBody, CategoryBody, CategoryBaseBody


class TestProductBody:
    def test_valid_product(self):
        p = ProductBody(name="Valid", price=Decimal("10.00"), quantity=5)
        assert p.name == "Valid"
        assert p.price == Decimal("10.00")

    def test_empty_name_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            ProductBody(name="   ", price=Decimal("10.00"))
        assert exc_info.value.field == "name"

    def test_name_stripped(self):
        p = ProductBody(name="  Trimmed  ", price=Decimal("10.00"))
        assert p.name == "Trimmed"

    def test_empty_description_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            ProductBody(name="Valid", price=Decimal("10.00"), description="   ")
        assert exc_info.value.field == "description"

    def test_none_description_ok(self):
        p = ProductBody(name="Valid", price=Decimal("10.00"), description=None)
        assert p.description is None

    def test_negative_price_raises(self):
        with pytest.raises(Exception):
            ProductBody(name="Valid", price=Decimal("-1.00"))

    def test_zero_price_raises(self):
        with pytest.raises(Exception):
            ProductBody(name="Valid", price=Decimal("0"))


class TestCategoryBaseBody:
    def test_valid_category(self):
        c = CategoryBaseBody(name="Category", description="Desc")
        assert c.name == "Category"

    def test_empty_name_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            CategoryBaseBody(name="   ")
        assert exc_info.value.field == "name"

    def test_empty_description_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            CategoryBaseBody(name="Valid", description="  ")
        assert exc_info.value.field == "description"


class TestCategoryBody:
    def test_empty_products_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            CategoryBody(name="Valid", products=[])
        assert exc_info.value.field == "products"

    def test_valid_with_products(self):
        c = CategoryBody(
            name="Valid",
            products=[ProductBody(name="P", price=Decimal("5.00"))],
        )
        assert len(c.products) == 1
