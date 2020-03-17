import numpy as np

from ..data import Order

COMMISSION_RATE = 0.015 / 100
TAX_RATE = 0.25 / 100

# Refer to the table at https://www.miraeassetdaewoo.com/hki/hki3061/n65.do
UNIT_PRICE_MAX = 1000
UNIT_PRICES = [(1000, 1), (5000, 5), (10000, 10),
               (50000, 50), (100000, 100), (500000, 500)]


def calc_commission(order: Order) -> float:
    return round(
        order.price *
        abs(order.quantity) *
        COMMISSION_RATE)


def calc_tax(order: Order) -> float:
    if order.quantity > 0:
        return 0
    else:
        return int(order.price * abs(order.quantity) * TAX_RATE)


def _get_unit_price(price: float) -> float:
    for p, u in UNIT_PRICES:
        if price < p:
            return u

    return UNIT_PRICE_MAX


def simulate_market_price(order: Order, slippage_stdev: float) -> float:
    offset = int(np.random.normal(
        0.5 if order.quantity > 0 else -0.5,
        slippage_stdev))

    unit_price = _get_unit_price(order.price)

    return order.price + unit_price * offset
