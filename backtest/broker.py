from logging import getLogger
from math import copysign
from multiprocessing import Value
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from typing import Callable

from .data import Msg
from .exchanges import Exchange

logger = getLogger(Path(__file__).stem)


class Broker(Thread):

    def __init__(self, cash: Value, exchange: Exchange) -> None:
        super().__init__(name=self.__class__.__name__)

        self.cash = cash
        self.initial_cash: float = cash.value
        self.exchange = exchange

        self.input: Connection
        self.output: Connection

        self._loop: bool = True
        self._handlers: dict[str, Callable[[Msg], None]] = {
            'ORDER': self._handler_order,
            'QUIT': self._handler_quit,
        }

        logger.debug('Initialized')

    def run(self):
        logger.debug('Starting...')

        self.output.send(Msg('CASH', cash=self.initial_cash))

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'Received: {msg}')
            self._handlers[msg.type](msg)

    def _handler_order(self, msg: Msg) -> None:
        fill = self.exchange.execute_order(msg)
        # A fill is the result of an order execution to buy or sell securities in the market.

        cost = self._calc_order_cost(fill)

        with self.cash.get_lock():
            self.cash.value -= cost
            fill.cash = self.cash.value

        self.output.send(fill)

        self.output.send(
            Msg('QUANTITY',
                symbol=fill.symbol, price=fill.price, quantity=fill.quantity))

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    @staticmethod
    def _calc_order_cost(msg: Msg) -> float:
        return copysign(1, msg.quantity) \
               * (abs(msg.quantity) * msg.price
                  + msg.commission
                  + msg.tax)
