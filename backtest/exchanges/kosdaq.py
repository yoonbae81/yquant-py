import logging

import numpy as np

logger = logging.getLogger('kospi')

RULES = {
    'commission': {
        'buy': 0.00015,
        'sell': 0.00015
    },
    'tax': {
        'buy': 0,
        'sell': 0.0025
    },
    'price_units': [
        {'price': 1000, 'unit': 1},
        {'price': 5000, 'unit': 5},
        {'price': 10000, 'unit': 10},
        {'price': 50000, 'unit': 50},
        {'price': 999999999, 'unit': 100}
    ]
}


def calc_commission(price, quantity) -> float:
    trade = 'buy' if quantity > 0 else 'sell'
    rate = RULES['commission'][trade]
    result = round(price * abs(quantity) * rate)
    logger.debug(f'Calculated commission')

    return result


def calc_tax(price, quantity) -> float:
    trade = 'buy' if quantity > 0 else 'sell'
    rate = RULES['tax'][trade]
    result = round(price * abs(quantity) * rate)
    logger.debug(f'Calculated tax')

    return result


def get_unit(price) -> float:
    items = RULES['price_units']
    for item in items:
        if price < item['price']:
            return item['unit']

    return items[-1]['unit']


def simulate_price(price, quantity) -> float:
    mean = 0.5 if quantity > 0 else -0.5,
    slippage_stdev = 0.7
    offset = int(np.random.normal(mean, slippage_stdev))

    unit = get_unit(price)
    result = price + offset * unit
    logger.debug('Simulated price')

    return result
