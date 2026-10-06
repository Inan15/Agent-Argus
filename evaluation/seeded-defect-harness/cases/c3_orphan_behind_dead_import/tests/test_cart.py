from src.cart import subtotal, orphan_behind_import  # imported, never called


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    assert result == 25
