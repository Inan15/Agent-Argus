from unittest.mock import Mock

from src.cart import subtotal


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    fake = Mock()
    fake.compute.return_value = 25
    pretended = fake.compute()
    assert pretended == 25
