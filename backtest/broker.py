import logging
from collections import defaultdict
from multiprocessing import Value
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from typing import Callable, DefaultDict

from .data import Msg, Position
from .exchanges import Exchange

logger = logging.getLogger(Path(__file__).stem)


class Broker(Thread):

    def __init__(self, cash: Value, exchange: Exchange) -> None:
        super().__init__(name=self.__class__.__name__)

        self.cash = cash
        self.initial_cash: float = cash.value
        self.exchange = exchange

        self._loop: bool = True

        self.input: Connection
        self.output: Connection

        self.positions: DefaultDict[str, Position] = defaultdict(Position)

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
        # self.cash -= order.total_cost
        # self.positions[msg.symbol].quantity += quantity

        # A fill is the result of an order execution to buy or sell securities in the market.
        fill: Msg = self.exchange.execute_order(msg)
        fill.cash = self.cash.value
        self.output.send(fill)

        # q: Msg = Msg('QUANTITY',
        #         symbol=msg.symbol,
        #         quantity=self._positions[msg.symbol].quantity)
        # self.output.send(q)

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    # def total_cost(self) -> float:
    #     return copysign(1, self.quantity) \
    #            * (abs(self.quantity) * self.price
    #               + self.commission
    #               + self.tax)
