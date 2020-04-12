import json
import logging
import queue
from datetime import datetime
from multiprocessing import Value, Event, Queue
from os.path import join
from pathlib import Path

from .data import Filled
from .market import kosdaq, kospi

logger = logging.getLogger('broker')


def run(config, cash, quantity_dict, order_queue, done: Event):
    symbols = _load_symbols(config['symbols_json'])
    ledger = _prepare_ledger(config['broker']['ledger_dir'])

    print(json.dumps({'cash': cash.value}), file=ledger)

    count = 0
    while not done.is_set():
        try:
            o = order_queue.get(block=True, timeout=1)
        except queue.Empty:
            continue

        market = (kospi if symbols.get(o.symbol, None) == 'KOSPI' else kosdaq)
        filled = _get_filled(config, market, o)

        _update_quantity(quantity_dict, filled)
        cash.value -= filled.total_cost()

        print(filled.as_json(), file=ledger)
        logger.debug('Wrote ' + repr(filled))

        count += 1

    ledger.close()
    logger.info(f'Processed {count} orders and wrote to {ledger.name}')


def _prepare_ledger(dir):
    Path(dir).mkdir(parents=True, exist_ok=True)
    name = f'{datetime.now():%Y%m%d%H%M%S}.jsonl'

    return open(join(dir, name), 'wt')


def _load_symbols(filepath):
    logger.info('Loading symbols list from ' + filepath)
    with open(filepath, 'rt') as f:
        symbols = json.load(f)

    return symbols


def _get_filled(config, market, order) -> Filled:
    price = market.simulate_market_price(order, config['broker']['slippage_stdev'])
    commission = market.calc_commission(order)
    tax = market.calc_tax(order)

    filled = Filled(
        order.symbol,
        order.quantity,
        price,
        commission,
        tax,
        order.price - price,
        order.timestamp,
    )

    return filled


def _update_quantity(quantity_dict, filled: Filled):
    quantity_dict.setdefault(filled.symbol, 0)
    quantity_dict[filled.symbol] += filled.quantity

    assert quantity_dict[filled.symbol] >= 0
