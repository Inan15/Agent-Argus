def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total


def apply_discount(total, rate):
    return total - (total * rate)
