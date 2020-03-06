from abc import ABC, abstractmethod
import time
from collections import namedtuple, defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd
import talib

from backtester import logger

Order = namedtuple('Order', 'symbol price quantity timestamp')


@dataclass
class Holding:
    quantity: float = 0
    bought: float = 0
    current: float = 0
    stoploss: float = 0


class Ticks(pd.DataFrame):
    def __init__(self, size=100, keep=30):
        super().__init__({'price': np.zeros(size, dtype=float),
                          'volume': np.zeros(size, dtype=float)})
        self._keep = keep
        self._watermark = -1
        self._timestamp = -1

    @property
    def _constructor(self):
        return Ticks

    def __iadd__(self, tick):
        if self._timestamp == tick.timestamp:
            self._update(tick)
        else:
            self._add(tick)

        return self

    def _update(self, tick):
        i = self._watermark
        self['price'][i] = tick.price
        self['volume'][i] += tick.volume

    def _add(self, tick):
        if len(self) == self._watermark + 1:
            self._erase_old()
            self._watermark = self._keep - 1

        i = self._watermark + 1
        self['price'][i] = tick.price
        self['volume'][i] = tick.volume
        self._timestamp = tick.timestamp
        self._watermark = i

    def _erase_old(self):
        for name in self.columns:
            arr = self[name]
            arr[:self._keep] = arr[-self._keep:]  # bring forward the given number of back items
            arr[self._keep:] = 0  # then make zero the remaining

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'columns={[col for col in self.columns]}, '
                f'length={len(self)}, '
                f'watermark={self._watermark}'
                f')')


class StrategyBase(ABC):

    def _calc_strength(self):
        pass

    def _calc_quantity(self):
        pass

    def _calc_stoploss(self):
        pass


def run(config, strategy, cash, holding_dict, tick_queue, order_queue, log_queue):
    logger.config(log_queue)

    ticks_dict = defaultdict(Ticks)

    count = 0
    while tick := tick_queue.get():
        ticks = ticks_dict[tick.symbol]
        ticks += tick

        if strength := strategy(ticks) >= config['threshold']:
            order = Order(tick.symbol,
                          tick.price,
                          1,
                          tick.timestamp)
            order_queue.put(order)

        count += 1

    logger.info(f'Analyzed {count} ticks')

    time.sleep(0.1)
    order_queue.put_nowait(None)
