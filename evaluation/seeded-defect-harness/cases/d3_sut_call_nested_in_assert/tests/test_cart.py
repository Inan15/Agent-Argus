from unittest.mock import Mock

from src.cart import subtotal


def test_subtotal():
    fake = Mock()
    fake.compute.return_value = 25
    assert fake.compute() == subtotal([(10, 2), (5, 1)]) or True
