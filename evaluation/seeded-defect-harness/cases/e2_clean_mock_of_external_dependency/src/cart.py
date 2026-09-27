def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total


def price_with_tax(items, tax_rate_source):
    """tax_rate_source is an injected dependency, e.g. a rates service."""
    rate = tax_rate_source.get_rate()
    return subtotal(items) * (1 + rate)
