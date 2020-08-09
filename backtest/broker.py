import logging
from collections import defaultdict
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from typing import Callable, DefaultDict

from .data import Msg, Position
from .exchanges import Exchange

logger = logging.getLogger(Path(__file__).stem)


class Broker(Thread):

    def __init__(self, cash: float, exchange: Exchange, calc_quantity) -> None:
        super().__init__(name=self.__class__.__name__)

        self._loop: bool = True
        self._initial_cash: float = cash

        self.input: Connection
        self.output: Connection

        self.cash: float = cash
        self.exchange = exchange
        self.calc_quantity = calc_quantity
        self.positions: DefaultDict[str, Position] = defaultdict(Position)

        self._handlers: dict[str, Callable[[Msg], None]] = {
            'SIGNAL': self._handler_signal,
            'QUIT': self._handler_quit,
        }

        logger.debug('Initialized')

    def run(self):
        logger.debug('Starting...')

        self.output.send(Msg('CASH', cash=self._initial_cash))

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'Received: {msg}')
            self._handlers[msg.type](msg)

    def _handler_signal(self, msg: Msg) -> None:
        quantity = self.calc_quantity(
            msg.price,
            msg.strength,
            self.cash,
            self.positions)

        # self.cash -= order.total_cost
        # self.positions[msg.symbol].quantity += quantity

        # A fill is the result of an order execution to buy or sell securities in the market.
        fill: Msg = self.exchange.order(msg.symbol, msg.price, quantity)
        fill.cash = self.cash
        fill.strength = msg.strength
        fill.timestamp = msg.timestamp
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
