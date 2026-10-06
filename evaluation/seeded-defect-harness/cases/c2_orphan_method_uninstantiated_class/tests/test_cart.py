from src.cart import subtotal


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    assert result == 25
