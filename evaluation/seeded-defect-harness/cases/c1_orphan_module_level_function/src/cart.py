def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total


def orphan_module_level(x):
    """Nothing in this repository calls this name."""
    return x * 3
