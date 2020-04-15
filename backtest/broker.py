import json
import logging
import queue
from datetime import datetime
from multiprocessing import Value, Event, Queue
from os.path import join
from pathlib import Path

import numpy as np

from .data import Filled

logger = logging.getLogger('broker')


def run(config, cash, quantity_dict, order_queue, done: Event):
    ledger = _prepare_ledger(config['broker']['ledger_dir'])
    print(json.dumps({'cash': cash.value}), file=ledger)

    count = 0
    while not done.is_set():
        try:
            order = order_queue.get(block=True, timeout=1)
            count += 1
        except queue.Empty:
            continue

        filled = _get_filled(config, order)
        cash.value -= filled.total_cost()
        quantity_dict[filled.symbol] = quantity_dict.get(filled.symbol, 0) \
                                       + filled.quantity

        print(filled.as_json(), file=ledger)
        logger.debug('Wrote ' + repr(filled))

    ledger.close()
    logger.info(f'Processed {count} orders and wrote to {ledger.name}')


def _prepare_ledger(dir):
    Path(dir).mkdir(parents=True, exist_ok=True)
    name = f'{datetime.now():%Y%m%d%H%M%S}.jsonl'

    return open(join(dir, name), 'wt')


def _get_filled(config, order) -> Filled:
    market = config['symbol'].get(order.symbol, 'KOSPI')
    price = _simulate_market_price(config, market, order.price, order.quantity)
    commission = _calc_commission(config, market, price, order.quantity)
    tax = _calc_tax(config, market, price, order.quantity)

    return Filled(
        order.symbol,
        market,
        order.quantity,
        price,
        commission,
        tax,
        order.price - price,
        order.timestamp,
    )


def _calc_commission(config, market, price, quantity) -> float:
    trade = 'buy' if quantity > 0 else 'sell'
    rate = config['market'][market]['commission'][trade]

    return round(price * abs(quantity) * rate)


def _calc_tax(config, market, price, quantity) -> float:
    trade = 'buy' if quantity > 0 else 'sell'
    rate = config['market'][market]['tax'][trade]

    return round(price * abs(quantity) * rate)


def _simulate_market_price(config, market, price, quantity) -> float:
    mean = 0.5 if quantity > 0 else -0.5,
    stdev = config['broker']['slippage_stdev']
    offset = int(np.random.normal(mean, stdev))

    price_unit = _get_price_unit(config, market, price)

    return price + offset * price_unit


def _get_price_unit(config, market, price) -> float:
    price_units = config['market'][market]['price_units']
    for item in price_units:
        if price < item['price']:
            return item['unit']

    return price_units[-1]['unit']
