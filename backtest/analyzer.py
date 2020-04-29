import logging
import os
from collections import defaultdict
from importlib import import_module
from multiprocessing import Process
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Dict, Callable, Set, DefaultDict

from .data import Timeseries, Msg

logger = logging.getLogger(Path(__file__).stem)

strategy = None


class Analyzer(Process):
    count: int = 0

    @classmethod
    def _get_name(cls) -> str:
        return cls.__name__ + str(cls.count)

    def __init__(self, strategy: str) -> None:
        self.__class__.count += 1
        super().__init__(name=self._get_name())

        self.input: Connection
        self.output: Connection

        self._strategy: str = strategy
        self._loop: bool = True
        self._stoploss: Dict = {}
        self._timeseries: DefaultDict[str, Timeseries] = defaultdict(Timeseries)

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'TICK': self._handler_tick,
            'QUANTITY': self._handler_quantity,
            'RESET': self._handler_reset,
            'QUIT': self._handler_quit,
        }

        logger.debug('Initialized ' + self.name)

    def run(self) -> None:
        logger.debug(self.name + f' started (pid:{os.getpid()})')

        global strategy
        logger.debug(f'Loading strategy module: {self._strategy}')
        strategy = import_module(f'.{self._strategy}', 'strategy')

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'{self.name} received: {msg}')

            self._handlers[msg.type](msg)

    def _handler_tick(self, msg: Msg) -> None:
        ts = self._timeseries[msg.symbol]
        ts += msg

        if msg.symbol in self._stoploss:
            stoploss_orig = self._stoploss[msg.symbol]
            self._stoploss[msg.symbol] = strategy.calc_stoploss(ts, stoploss_orig)

        strength = strategy.calc_strength(
            ts,
            self._stoploss.get(msg.symbol, None))

        s = Msg('SIGNAL',
                symbol=msg.symbol,
                price=msg.price,
                strength=strength,
                timestamp=msg.timestamp)

        self.output.send(s)

    def _handler_quantity(self, msg: Msg) -> None:
        if msg.quantity == 0 and msg.symbol in self._stoploss:
            del self._stoploss[msg.symbol]
        else:
            ts = self._timeseries[msg.symbol]
            stoploss_orig = self._stoploss.get(msg.symbol, None)
            self._stoploss[msg.symbol] = strategy.calc_stoploss(ts, stoploss_orig)

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    def _handler_reset(self, _: Msg) -> None:
        [s.erase() for s in self._timeseries.values()]
