from unittest.mock import Mock

from src.cart import price_with_tax


def test_price_with_tax_applies_the_injected_rate():
    fake_rate_source = Mock()
    fake_rate_source.get_rate.return_value = 0.1
    result = price_with_tax([(10, 2), (5, 1)], fake_rate_source)
    assert result == 27.5
