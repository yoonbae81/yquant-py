from backtester.data import Order


def calc_commission(order: Order):
    return 1


def calc_tax(order: Order):
    return 1


def simulate_market_order(order: Order):
    return order.price
