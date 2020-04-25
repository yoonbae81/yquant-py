from json import dumps
from math import copysign
from collections import namedtuple
from dataclasses import dataclass, asdict

import numpy as np

Tick = namedtuple('Tick',
                  'symbol price volume timestamp')
RESET = Tick('[RESET]', 0, 0, 0)

Signal = namedtuple('Signal',
                    'symbol market price strength timestamp')


@dataclass
class Msg:
    type: str = ''
    symbol: str = ''
    market: str = ''
    price: float = 0
    quantity: float = 0
    strength: int = 0
    timestamp: int = 0


@dataclass
class Order:
    symbol: str
    market: str
    price: float
    quantity: float
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
    def __init__(self, symbol: str, market: str, name: str = '', size: int = 100, keep: int = 30):
        self.symbol = symbol
        self.market = market
        self.name = name
        self.stoploss = None

        self._size = size
        self._keep = keep
        self._watermark = -1
        self._timestamp = -1
        self._timeseries = {'price': np.zeros(size, dtype=float),
                            'quantity': np.zeros(size, dtype=float)}

    def add_timeseries(self, key):
        self._timeseries[key] = np.zeros(self._size, dtype=float)

    def erase_timeseries(self):
        for arr in self._timeseries.values():
            arr[:] = 0

    def __getitem__(self, key):
        return self._timeseries[key]

    def __len__(self):
        return self._size

    def __iadd__(self, msg: Msg) -> 'Stock':
        if self._timestamp == msg.timestamp:
            self._update(msg)
        else:
            self._add(msg)

        return self

    def _update(self, msg: Msg) -> None:
        i = self._watermark
        self['price'][i] = msg.price
        self['quantity'][i] += msg.quantity

    def _add(self, msg: Msg) -> None:
        if len(self) == self._watermark + 1:
            self._erase_old()
            self._watermark = self._keep - 1

        i = self._watermark + 1
        self['price'][i] = msg.price
        self['quantity'][i] = msg.quantity
        self._timestamp = msg.timestamp
        self._watermark = i

    def _erase_old(self) -> None:
        for arr in self._timeseries.values():
            # bring forward the given number of back items
            arr[:self._keep] = arr[-self._keep:]
            arr[self._keep:] = 0  # then make zero the remaining

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}('
                f'columns={[key for key in self._timeseries]}, '
                f'length={len(self)}, '
                f'watermark={self._watermark}, '
                f'stoploss={self.stoploss}'
                f')')
