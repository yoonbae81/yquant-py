import logging
from collections import defaultdict
from importlib import import_module
from math import copysign
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from typing import Callable, DefaultDict

from .data import Msg, Order, Position

logger = logging.getLogger(Path(__file__).stem)


class Broker(Thread):

    def __init__(self, cash: float, symbols: dict, exchanges: list, rates: dict, calc_quantity) -> None:
        super().__init__(name=self.__class__.__name__)

        self.input: Connection
        self.output: Connection

        self.calc_quantity = calc_quantity

        self._loop: bool = True
        self._current_cash: float = cash
        self._initial_cash: float = cash
        self._positions: DefaultDict[str, Position] = defaultdict(Position)
        self._symbols: dict[str, dict] = symbols
        self.rates: dict = rates

        self._handlers: dict[str, Callable[[Msg], None]] = {
            'SIGNAL': self._handler_signal,
            'QUIT': self._handler_quit,
        }

        logger.debug('Loading modules...')
        self.exchanges = {}
        for exchange in exchanges:
            self.exchanges[exchange] = import_module(f'{exchange}')

        logger.debug('Initialized')

    def run(self):
        logger.debug('Starting...')

        self.output.send(Msg('CASH', cash=self._initial_cash))

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'Received: {msg}')
            self._handlers[msg.type](msg)

    def _get_exchange(self, symbol):
        try:
            exchange = self._symbols[symbol]['exchange']
            return self.exchanges[exchange]
        except KeyError:
            logger.warning(f'Unknown symbol: {symbol}')
            return next(iter(self.exchanges.values()))  # the first one

    def _handler_signal(self, msg: Msg) -> None:

        exchange = self._get_exchange(msg.symbol)

        quantity = self.calc_quantity(
            msg.price,
            msg.strength,
            self._current_cash,
            self._positions)

        price = exchange.simulate_price(
            msg.price,
            quantity)

        order = Order(msg.symbol,
                      price,
                      quantity,
                      self.rates)

        self._current_cash -= order.total_cost

        # self._positions[msg.symbol].quantity += quantity

        o = Msg("ORDER",
                symbol=msg.symbol,
                price=price,
                quantity=quantity,
                strength=msg.strength,
                commission=order.commission,
                tax=order.tax,
                slippage=msg.price - price,
                cash=self._current_cash,
                timestamp=msg.timestamp)
        self.output.send(o)

        # q = Msg('QUANTITY',
        #         symbol=msg.symbol,
        #         quantity=self._positions[msg.symbol].quantity)
        # self.output.send(q)

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

