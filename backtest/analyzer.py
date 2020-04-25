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

    def __init__(self) -> None:
        self.__class__.count += 1
        name: str = self.__class__.__name__ + str(self.__class__.count)
        super().__init__(name=name)

        self.input: Connection
        self.output: Connection

        self._loop: bool = True

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

    def _handler_tick(self, msg: Msg) -> None:
        msg.type = 'SIGNAL'
        msg.strength = randint(-10, 10)

        self.output.send(msg)

    def _handler_quantity(self, msg: Msg) -> None:
        if msg.quantity == 0 and msg.symbol in self._opened:
            self._opened.remove(msg.symbol)
        else:
            self._opened.add(msg.symbol)

    def _handler_quit(self, msg: Msg) -> None:
        self._loop = False

    def _handler_reset(self, msg: Msg) -> None:
        pass


def run(symbols, strategy, quantity_dict, tick_queue, signal_queue, done: Event):
    stock_dict = {}
    count = 0
    while not done.is_set():
        try:
            tick = tick_queue.get(block=True, timeout=1)
        except queue.Empty:
            continue

        if tick == RESET:
            [s.erase_timeseries() for s in stock_dict.values()]
            continue

        try:
            stock = stock_dict[tick.symbol]
        except KeyError:
            stock = Stock(tick.symbol, symbols.get(tick.symbol, 'KOSPI'))
            stock_dict[tick.symbol] = stock

        stock += tick
        count += 1

        holding = quantity_dict.get(tick.symbol, 0)
        if holding > 0:
            stock.stoploss = strategy.calc_stoploss(stock)

        strength = strategy.calc_strength(stock)
        signal = Signal(stock.symbol,
                        stock.market,
                        tick.price,
                        strength,
                        tick.timestamp)
        signal_queue.put(signal)

    logger.info(f'Analyzed {count} ticks')
