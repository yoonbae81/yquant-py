import json
import queue

from multiprocessing import Event, Process
from multiprocessing.connection import Connection
from pathlib import Path

import logging
from random import randint
from typing import Dict, Callable, Set

from .data import Tick, RESET, Stock, Signal, Msg

logger = logging.getLogger('analyzer')


class Analyzer(Process):
    count: int = 0

    @classmethod
    def _get_name(cls) -> str:
        return cls.__name__ + str(cls.count)

    def __init__(self, strategy, symbols: Dict[str, Dict]) -> None:
        self.__class__.count += 1
        super().__init__(name=self._get_name())

        self._strategy = strategy
        self._symbols = symbols

        self.input: Connection
        self.output: Connection

        self._loop: bool = True
        self._stocks: Dict[str, Stock] = {}

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'TICK': self._handler_tick,
            'QUANTITY': self._handler_quantity,
            'RESET': self._handler_reset,
            'QUIT': self._handler_quit,
        }

        self._opened: Set[str] = set()  # Opened positions

        logger.debug(self._name + ' initialized')

    def run(self) -> None:
        while self._loop:
            msg = self.input.recv()
            logger.debug(f'{self.name} received: {msg}')

            self._handlers[msg.type](msg)

    def _get_market(self, msg: Msg) -> str:
        market: str
        try:
            market = self._symbols[msg.symbol]['market']
        except KeyError:
            market = 'KOSPI'

        return market

    def _get_stock(self, msg: Msg) -> Stock:
        stock: Stock
        try:
            stock = self._stocks[msg.symbol]
        except KeyError:
            stock = Stock(msg.symbol, msg.market)
            self._stocks[msg.symbol] = stock

        return stock

    def _handler_tick(self, msg: Msg) -> None:
        msg.market = self._get_market(msg)
        stock = self._get_stock(msg)

        stock += msg

        if msg.symbol in self._opened:
            stock.stoploss = self._strategy.calc_stoploss(stock)

        msg.strength = self._strategy.calc_strength(stock)
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
        [s.erase_timeseries() for s in self._stocks.values()]
