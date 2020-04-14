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
    market = (kospi
              if config['symbols'].get(order.symbol, None) == 'KOSPI'
              else kosdaq)

    price = market.simulate_market_price(order, config['broker']['slippage_stdev'])
    commission = market.calc_commission(order)
    tax = market.calc_tax(order)

    return Filled(
        order.symbol,
        order.quantity,
        price,
        commission,
        tax,
        order.price - price,
        order.timestamp,
    )
