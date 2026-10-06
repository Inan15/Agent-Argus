def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total
