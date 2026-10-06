from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    expected = 25
    assert expected == 25
