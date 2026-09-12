from src.cart import subtotal, apply_discount


def test_subtotal_sums_price_times_quantity():
    assert subtotal([(10, 2), (5, 1)]) == 25


def test_subtotal_empty_cart_is_zero():
    assert subtotal([]) == 0


def test_apply_discount_reduces_total_by_rate():
    assert apply_discount(100, 0.2) == 80
