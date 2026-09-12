from unittest.mock import Mock

from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    fake = Mock()
    fake.compute(25)
    fake.compute.assert_called_once_with(25)
