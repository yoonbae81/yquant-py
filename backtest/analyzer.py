import os
from collections import defaultdict
from logging import getLogger
from multiprocessing import Process, Value
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Callable, DefaultDict

from .data import Msg, Position, Timeseries
from .strategies import Strategy

logger = getLogger(Path(__file__).stem)

strategy = None


class Analyzer(Process):
    count: int = 0

    @classmethod
    def _get_name(cls) -> str:
        return cls.__name__ + str(cls.count)

    def __init__(self, cash: Value, strategy: Strategy):
        self.__class__.count += 1
        super().__init__(name=self._get_name())

        self.cash = cash
        self.initial_cash: float = cash.value
        self.strategy = strategy

        self.input: Connection
        self.output: Connection

        self.position_dict: DefaultDict[str, Position] = defaultdict(Position)
        self.timeseries_dict: DefaultDict[str,
                                          Timeseries] = defaultdict(Timeseries)

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
        timeseries = self.timeseries_dict[msg.symbol]
        timeseries += msg

        position = self.position_dict[msg.symbol]

        if order := self.strategy.handle(msg, self.cash.value, timeseries, position):
            self.output.send(order)

    def _handler_quantity(self, msg: Msg) -> None:
        position = self.position_dict.get(msg.symbol, None)

        if not position:  # newly opened positions
            position = Position(msg.price, msg.quantity)
            self.position_dict[msg.symbol] = position
        else:
            position.add(msg.price, msg.quantity)

        if position.quantity == 0:  # closed all positions
            del self.position_dict[msg.symbol]

        logger.debug(f'{msg.symbol}: {self.position_dict.get(msg.symbol)}')

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    def _handler_reset(self, _: Msg) -> None:
        [s.erase() for s in self.timeseries_dict.values()]
