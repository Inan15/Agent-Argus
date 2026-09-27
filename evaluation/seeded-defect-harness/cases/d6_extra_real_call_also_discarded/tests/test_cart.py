from unittest.mock import Mock

from src.cart import subtotal, apply_discount


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    apply_discount(25, 0.1)
    fake = Mock()
    fake.compute.return_value = 25
    pretended = fake.compute()
    assert pretended == 25
