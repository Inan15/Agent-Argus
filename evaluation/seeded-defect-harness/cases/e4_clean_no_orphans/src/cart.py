def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total


def price_summary(items):
    """Used by tests below -- not an orphan."""
    return f"total: {subtotal(items)}"
