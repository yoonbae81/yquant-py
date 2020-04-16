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


def run(rules, cash, quantity_dict, order_queue, ledger_dir, done: Event):
    ledger = _prepare_ledger(ledger_dir)
    print(json.dumps({'cash': cash.value}), file=ledger)

    count = 0
    while not done.is_set():
        try:
            order = order_queue.get(block=True, timeout=1)
            count += 1
        except queue.Empty:
            continue

        filled = _get_filled(order, rules)
        cash.value -= filled.total_cost()
        quantity_dict[filled.symbol] = quantity_dict.get(filled.symbol, 0) \
                                       + filled.quantity

        print(filled.as_json(), file=ledger)
        logger.debug('Wrote ' + repr(filled))

    ledger.close()
    logger.info(f'Processed {count} orders and wrote to {ledger.name}')


def _prepare_ledger(dir):
    path = Path(dir)
    path.mkdir(parents=True, exist_ok=True)
    filename = f'{datetime.now():%Y%m%d%H%M%S}.jsonl'

    return path.joinpath(filename).open('wt')


def _get_filled(order, rules) -> Filled:
    price = _simulate_market_price(order.price,
                                   order.quantity,
                                   rules[order.market]['price_units'])
    commission = _calc_commission(price,
                                  order.quantity,
                                  rules[order.market]['commission'])
    tax = _calc_tax(price,
                    order.quantity,
                    rules[order.market]['tax'])

    return Filled(
        order.symbol,
        order.market,
        price,
        order.quantity,
        commission,
        tax,
        order.price - price,
        order.timestamp,
    )


def _simulate_market_price(price, quantity, price_units, slippage_stdev=0.7) -> float:
    mean = 0.5 if quantity > 0 else -0.5,
    offset = int(np.random.normal(mean, slippage_stdev))
    price_unit = _get_price_unit(price, price_units)

    return price + offset * price_unit


def _get_price_unit(price, price_units) -> float:
    for item in price_units:
        if price < item['price']:
            return item['unit']

    return price_units[-1]['unit']


def _calc_commission(price, quantity, rates) -> float:
    trade = 'buy' if quantity > 0 else 'sell'
    rate = rates[trade]

    return round(price * abs(quantity) * rate)


def _calc_tax(price, quantity, rates) -> float:
    trade = 'buy' if quantity > 0 else 'sell'
    rate = rates[trade]

    return round(price * abs(quantity) * rate)
