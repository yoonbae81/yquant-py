import logging
from collections import defaultdict
from importlib import import_module
from math import copysign
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from typing import Callable, Dict, DefaultDict

from .data import Msg, Positions

logger = logging.getLogger(Path(__file__).stem)

market = None
strategy = None


class Broker(Thread):

    def __init__(self, market: str, strategy: str, cash: float) -> None:
        super().__init__(name=self.__class__.__name__)

        self.input: Connection
        self.output: Connection

        self._loop: bool = True
        self._market: str = market
        self._strategy: str = strategy
        self._cash: float = cash
        self._initial_cash: float = cash
        self._positions: Positions = Positions()

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'SIGNAL': self._handler_signal,
            'QUIT': self._handler_quit,
        }

        logger.debug('Initialized')

    def run(self):
        logger.debug('Started')

        global market
        logger.debug(f'Loading market module: {self._market}')
        market = import_module(f'.{self._market}', 'market')

        global strategy
        logger.debug(f'Loading strategy module: {self._strategy}')
        strategy = import_module(f'.{self._strategy}', 'strategy')

        self.output.send(Msg('CASH', cash=self._initial_cash))

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'Received: {msg}')
            self._handlers[msg.type](msg)

    def _handler_signal(self, msg: Msg) -> None:
        quantity = strategy.calc_quantity(
            msg.price,
            msg.strength,
            self._cash,
            self._positions)

        exchange = market.get_exchange(msg.symbol)

        price = market.simulate_price(
            exchange,
            msg.price,
            quantity)

        commission = market.calc_commission(
            exchange,
            price,
            quantity)

        tax = market.calc_tax(
            exchange,
            price,
            quantity)

        self._cash -= self._calc_total_cost(price, quantity, commission, tax)
        self._positions[msg.symbol].quantity += quantity

        o = Msg("ORDER",
                symbol=msg.symbol,
                price=price,
                quantity=quantity,
                strength=msg.strength,
                commission=commission,
                tax=tax,
                slippage=msg.price - price,
                cash=self._cash,
                timestamp=msg.timestamp)
        self.output.send(o)

        q = Msg('QUANTITY',
                symbol=msg.symbol,
                quantity=self._positions[msg.symbol].quantity)
        self.output.send(q)

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    @staticmethod
    def _calc_total_cost(price: float, quantity: float, commission: float, tax: float) -> float:
        return copysign(1, quantity) \
               * (abs(quantity)
                  * price
                  + commission
                  + tax)
