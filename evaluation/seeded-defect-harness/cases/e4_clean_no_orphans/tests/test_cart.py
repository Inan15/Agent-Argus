from src.cart import subtotal, price_summary


def test_subtotal():
    assert subtotal([(10, 2), (5, 1)]) == 25


def test_price_summary_formats_the_total():
    assert price_summary([(10, 2), (5, 1)]) == "total: 25"
