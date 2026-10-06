def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total


class PricingHelper:
    """Nothing in this repository ever instantiates PricingHelper."""

    def orphan_method(self, x):
        return x * 4
