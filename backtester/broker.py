import json
from collections import defaultdict
from datetime import datetime
from multiprocessing import Value
from os.path import join
from pathlib import Path

from backtester import logger

from backtester.data import Order
from backtester.market import kosdaq, kospi


def buy(order: Order, cash: Value, quantity_dict: dict):
    tax = kosdaq.calc_tax(order)
    commission = kosdaq.calc_commission(order)

    if order.symbol not in quantity_dict:
        quantity_dict[order.symbol] = 0

    quantity_dict[order.symbol] += order.quantity
    cash.value -= order.price * order.quantity + tax + commission
    assert cash.value >= 0


def sell(order: Order, cash: Value, quantity_dict: dict):
    pass


def _get_filepath(dir: str, dt: datetime):
    Path(dir).mkdir(parents=True, exist_ok=True)
    return join(dir, f'{dt:%Y%m%d%H%M%S}.jsonl')


def run(config, cash, holding_dict, order_queue, log_queue):
    logger.config(log_queue)

    logger.debug("TODO open a file")
    filepath = _get_filepath(config['ledger_dir'], datetime.now())
    ledger = open(filepath, 'wt')
    print(json.dumps({'cash': cash.value}), file=ledger)

    count = 0
    while order := order_queue.get():
        logger.info(order)

        fn = buy if order.quantity >= 0 else sell
        fn(order, cash, holding_dict)

        ''' TODO
        example of record
            record = {'timestamp': 1,
                      'symbol': '015760',
                      'price': 20000.0,
                      'quantity': 4,
                      'cost': 221,
                      'slippage': 500.0}
        '''

        logger.debug('Ledger: ' + json.dumps(order._asdict()))
        print(json.dumps(order._asdict()), file=ledger)

        count += 1

    ledger.close()
    logger.info(f'Processed {count} orders')
    logger.info(f'Remaining cash: {cash.value}')
    logger.info(f'Wrote {count:,d} records to {filepath}')
    logger.info(holding_dict)
