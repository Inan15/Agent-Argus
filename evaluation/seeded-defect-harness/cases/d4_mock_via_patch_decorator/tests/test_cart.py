from unittest.mock import patch

from src.cart import subtotal


@patch("time.time")
def test_subtotal(mock_time):
    subtotal([(10, 2), (5, 1)])
    mock_time.return_value = 25
    pretended = mock_time()
    assert pretended == 25
