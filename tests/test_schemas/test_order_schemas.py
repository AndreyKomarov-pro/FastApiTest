from decimal import Decimal
from uuid import uuid4

import pytest

from src.enums.order_status import OrderStatus
from src.exceptions.validation import ValidationException
from src.schemas.order import OrderBody, OrderEntryBody, OrderUpdateBody


class TestOrderEntryBody:
    def test_valid_entry(self):
        e = OrderEntryBody(product_id=uuid4(), quantity=2, price=Decimal("10.00"))
        assert e.quantity == 2

    def test_zero_quantity_raises(self):
        with pytest.raises(Exception):
            OrderEntryBody(product_id=uuid4(), quantity=0, price=Decimal("10.00"))

    def test_negative_price_raises(self):
        with pytest.raises(Exception):
            OrderEntryBody(product_id=uuid4(), quantity=1, price=Decimal("-5.00"))

    def test_default_quantity(self):
        e = OrderEntryBody(product_id=uuid4(), price=Decimal("10.00"))
        assert e.quantity == 1


class TestOrderBody:
    def test_valid_order(self):
        o = OrderBody(
            user_id=uuid4(),
            items=[OrderEntryBody(product_id=uuid4(), price=Decimal("10.00"))],
        )
        assert len(o.items) == 1

    def test_empty_items_raises(self):
        with pytest.raises(ValidationException) as exc_info:
            OrderBody(user_id=uuid4(), items=[])
        assert exc_info.value.field == "items"


class TestOrderUpdateBody:
    def test_valid_status(self):
        u = OrderUpdateBody(status=OrderStatus.PAID)
        assert u.status == OrderStatus.PAID

    def test_none_status_ok(self):
        u = OrderUpdateBody()
        assert u.status is None

    def test_invalid_status_raises(self):
        with pytest.raises(Exception):
            OrderUpdateBody(status="INVALID")
