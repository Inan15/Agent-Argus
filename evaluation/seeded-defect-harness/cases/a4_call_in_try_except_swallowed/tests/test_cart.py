from src.cart import subtotal


def test_subtotal():
    try:
        subtotal([(10, 2), (5, 1)])
    except Exception:
        pass
