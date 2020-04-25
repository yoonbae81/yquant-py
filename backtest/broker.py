import json
import logging
import queue
from datetime import datetime
from multiprocessing import Value, Event, Queue
from multiprocessing.connection import Connection
from os.path import join
from pathlib import Path
from threading import Thread
from typing import Callable, Dict

import numpy as np

from .data import Order, Msg

logger = logging.getLogger('broker')


class Broker(Thread):
    def __init__(self) -> None:
        super().__init__(name=self.__class__.__name__)

        self.input: Connection
        self.output: Connection

        self._loop: bool = True

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'SIGNAL': self._handler_signal,
            'QUIT': self._handler_quit,
        }

        logger.debug(self._name + ' initialized')

    def run(self):
        while self._loop:
            msg = self.input.recv()
            logger.debug(f'{self.name} received: {msg}')
            self._handlers[msg.type](msg)

    def _handler_signal(self, msg: Msg) -> None:
        msg.type = 'QUANTITY'
        self.output.send(msg)

    def _handler_quit(self, msg: Msg) -> None:
        self._loop = False


def run(rules, strategy, initial_cash, quantity_dict, signal_queue, ledger_dir, done: Event):
    ledger = _prepare_ledger(ledger_dir)
    print(json.dumps({'cash': initial_cash}), file=ledger)
    cash = initial_cash

    count = 0
    while not done.is_set():
        try:
            signal = signal_queue.get(block=True, timeout=1)
            count += 1
        except queue.Empty:
            continue

        quantity = strategy.calc_quantity(signal, cash, quantity_dict)

        price = _simulate_market_price(signal.price,
                                       quantity,
                                       rules[signal.market]['price_units'])

        commission = _calc_commission(price,
                                      quantity,
                                      rules[signal.market]['commission'])

        tax = _calc_tax(price,
                        quantity,
                        rules[signal.market]['tax'])

        order = Order(
            signal.symbol,
            signal.market,
            price,
            quantity,
            commission,
            tax,
            signal.price - price,
            signal.timestamp,
        )

        initial_cash -= order.total_cost()
        quantity_dict[order.symbol] = quantity_dict.get(signal.symbol, 0) \
                                      + order.quantity

        print(order.as_json(), file=ledger)
        logger.debug('Wrote ' + repr(order))

    ledger.close()
    logger.info(f'Processed {count} orders and wrote to {ledger.name}')


def _prepare_ledger(dir):
    path = Path(dir)
    path.mkdir(parents=True, exist_ok=True)
    filename = f'{datetime.now():%Y%m%d%H%M%S}.jsonl'

    return path.joinpath(filename).open('wt')


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
