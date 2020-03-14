import numpy as np

from ..data import Order

COMMISSION_RATE = 0.015 / 100
TAX_RATE = 0.25 / 100

# Refer to the table at https://www.miraeassetdaewoo.com/hki/hki3061/n65.do
UNIT_PRICE_MAX = 100
UNIT_PRICES = dict(zip([1000, 5000, 10000, 50000],
                       [1, 5, 10, 50]))


def calc_commission(order: Order):
    return round(
        order.price *
        abs(order.quantity) *
        COMMISSION_RATE)


def calc_tax(order: Order):
    if order.quantity > 0:
        return 0
    else:
        return int(order.price * abs(order.quantity) * TAX_RATE)


def _get_unit_price(price: float):
    for p, u in UNIT_PRICES.items():
        if price < p:
            return u

    return UNIT_PRICE_MAX


def simulate_market_price(order: Order, slippage_stdev: float):
    mean = 0.5 if order.quantity > 0 else -0.5
    offset = round(np.random.normal(mean, slippage_stdev))
    unit_price = _get_unit_price(order.price)
    return order.price + unit_price * offset
