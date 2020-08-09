import os
from logging import getLogger
from collections import defaultdict
from multiprocessing import Process, Value
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Callable, DefaultDict

from .data import Timeseries, Msg, Position

logger = getLogger(Path(__file__).stem)

strategy = None


class Analyzer(Process):
    count: int = 0

    @classmethod
    def _get_name(cls) -> str:
        return cls.__name__ + str(cls.count)

    def __init__(self, cash: Value, calc_strength, calc_stoploss, calc_quantity):
        self.__class__.count += 1
        super().__init__(name=self._get_name())

        self.cash = cash
        self.initial_cash: float = cash.value
        self.calc_strength = calc_strength
        self.calc_stoploss = calc_stoploss
        self.calc_quantity = calc_quantity

        self.input: Connection
        self.output: Connection

        self._stoploss: dict[str, float] = {}
        self.positions: dict[str, Position] = {}
        self.timeseries: DefaultDict[str, Timeseries] = defaultdict(Timeseries)

        self._loop: bool = True
        self._handlers: dict[str, Callable[[Msg], None]] = {
            'TICK': self._handler_tick,
            'QUANTITY': self._handler_quantity,
            'RESET': self._handler_reset,
            'QUIT': self._handler_quit,
        }

        logger.debug('Initialized ' + self.name)

    def run(self) -> None:
        logger.debug(self.name + f' starting (pid:{os.getpid()})...')

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'{self.name} received: {msg}')

            self._handlers[msg.type](msg)

    def _handler_tick(self, msg: Msg) -> None:

        position = self.positions.get(msg.symbol, None)

        ts = self.timeseries[msg.symbol]
        ts += msg

        if position:
            position.stoploss = self.calc_stoploss(ts, position.stoploss)

        strength = self.calc_strength(
            ts,
            self._stoploss.get(msg.symbol, None))

        order = Msg('ORDER',
                    symbol=msg.symbol,
                    price=msg.price,
                    strength=strength,
                    timestamp=msg.timestamp)

        order.quantity = self.calc_quantity(
            msg.price,
            msg.strength,
            self.initial_cash,
            self.cash.value)

        self.output.send(order)

    def _handler_quantity(self, msg: Msg) -> None:
        position = self.positions.get(msg.symbol, None)

        if not position:  # newly opened positions
            position = Position(msg.price, msg.quantity)
            self.positions[msg.symbol] = position
        else:
            position.add(msg.price, msg.quantity)

        if position.quantity == 0:  # closed all positions
            del self.positions[msg.symbol]

        logger.debug(f'{msg.symbol}: {self.positions.get(msg.symbol, None)}')

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    def _handler_reset(self, _: Msg) -> None:
        [s.erase() for s in self.timeseries.values()]
