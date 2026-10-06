def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total


def orphan_behind_import(x):
    """Imported by tests/test_cart.py but never actually called."""
    return x * 5
