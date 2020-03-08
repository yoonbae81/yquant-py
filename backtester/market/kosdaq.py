import numpy as np

from backtester.data import Order
from backtester.market import kospi

# Refer to the table at https://www.miraeassetdaewoo.com/hki/hki3061/n65.do
UNIT_PRICE_MAX = 100
UNIT_PRICES = dict(zip([1000, 5000, 10000, 50000, 100000],
                       [1, 5, 10, 50, 100]))

calc_commission = kospi.calc_commission
calc_tax = kospi.calc_tax


def _get_unit_price(price):
    for p, u in UNIT_PRICES.items():
        if price < p:
            return u

    return UNIT_PRICE_MAX


def simulate_market_price(order: Order):
    unit_price = _get_unit_price(order.price)
    deviation = round(np.random.normal(0, 1))
    return order.price + unit_price * deviation
