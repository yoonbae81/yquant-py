from json import dumps
from math import copysign
from collections import namedtuple
from dataclasses import dataclass, asdict

import numpy as np

Tick = namedtuple('Tick',
                  'symbol price volume timestamp')
Order = namedtuple('Order',
                   'symbol price quantity timestamp')


@dataclass
class Filled:
    symbol: str
    market: str
    quantity: float
    price: float
    commission: float
    tax: float
    slippage: float
    timestamp: int

    def total_cost(self):
        return copysign(1, self.quantity) \
               * (abs(self.quantity)
                  * self.price
                  + self.commission
                  + self.tax)

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return dumps(asdict(self))


class Stock:
    def __init__(self, size=100, keep=30):
        self.stoploss = None

        self._size = size
        self._keep = keep
        self._watermark = -1
        self._timestamp = -1
        self._timeseries = {'price': np.zeros(size, dtype=float),
                            'volume': np.zeros(size, dtype=float)}

    def add_timeseries(self, key):
        self._timeseries[key] = np.zeros(self._size, dtype=float)

    def __getitem__(self, key):
        return self._timeseries[key]

    def __len__(self):
        return self._size

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
        for key in self._timeseries.keys():
            arr = self._timeseries[key]
            arr[:self._keep] = arr[-self._keep:]  # bring forward the given number of back items
            arr[self._keep:] = 0  # then make zero the remaining

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'columns={[key for key in self._timeseries]}, '
                f'length={len(self)}, '
                f'watermark={self._watermark}, '
                f'stoploss={self.stoploss}'
                f')')
