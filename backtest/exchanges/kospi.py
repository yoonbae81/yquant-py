import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(Path(__file__).stem)

DEFAULTS = {
    'price_units': [
        {'price': 1000, 'unit': 1},
        {'price': 5000, 'unit': 5},
        {'price': 10000, 'unit': 10},
        {'price': 50000, 'unit': 50},
        {'price': 100000, 'unit': 100},
        {'price': 500000, 'unit': 500},
        {'price': 999999999, 'unit': 1000}
    ]
}


def get_unit(price) -> float:
    items = DEFAULTS['price_units']
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
