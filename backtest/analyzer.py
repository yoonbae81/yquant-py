import logging
from importlib import import_module
from multiprocessing import Process
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Dict, Callable, Set

from .data import Timeseries, Msg

logger = logging.getLogger(Path(__file__).name)


class Analyzer(Process):
    count: int = 0

    @classmethod
    def _get_name(cls) -> str:
        return cls.__name__ + str(cls.count)

    def __init__(self, strategy: str) -> None:
        self.__class__.count += 1
        super().__init__(name=self._get_name())

        # self._strategy = strategy

        self.input: Connection
        self.output: Connection

        self._loop: bool = True
        self._stocks: Dict[str, Timeseries] = {}
        self._opened: Set[str] = set()  # Opened positions
        self._strategy: str = strategy

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'TICK': self._handler_tick,
            'QUANTITY': self._handler_quantity,
            'RESET': self._handler_reset,
            'QUIT': self._handler_quit,
        }

        logger.debug(self.name + ' initialized')

    def run(self) -> None:
        logger.debug(self.name + ' started')

        logger.debug(f'Loading strategy: {self._strategy}')
        self._strategy_module = import_module(self._strategy)

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'{self.name} received: {msg}')

            self._handlers[msg.type](msg)

    def _get_stock(self, msg: Msg) -> Timeseries:
        stock: Timeseries
        try:
            stock = self._stocks[msg.symbol]
        except KeyError:
            stock = Timeseries()
            self._stocks[msg.symbol] = stock

        return stock

    def _handler_tick(self, msg: Msg) -> None:
        stock = self._get_stock(msg)
        stock += msg

        if msg.symbol in self._opened:
            stock.stoploss = self._strategy_module.calc_stoploss(stock)

        msg.strength = self._strategy_module.calc_strength(stock)
        msg.type = 'SIGNAL'

        self.output.send(msg)

    def _handler_quantity(self, msg: Msg) -> None:
        if msg.quantity == 0 and msg.symbol in self._opened:
            self._opened.remove(msg.symbol)
        else:
            self._opened.add(msg.symbol)

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    def _handler_reset(self, _: Msg) -> None:
        [s.erase() for s in self._stocks.values()]
