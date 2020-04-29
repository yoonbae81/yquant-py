from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Optional

import numpy as np


@dataclass
class Msg:
    type: str = ''
    symbol: str = ''
    price: float = 0
    quantity: float = 0
    strength: int = 0  # analyzer
    cash: float = 0  # broker
    commission: float = 0  # broker, ledge
    tax: float = 0  # broker, ledge
    slippage: float = 0  # broker, ledge
    timestamp: int = 0




@dataclass
class Stock:
    price: float = 0
    quantity: float = 0
    stoploss: float = 0


class Positions:
    def __init__(self) -> None:
        self._stocks: DefaultDict[str, Stock] = defaultdict(Stock)

    def __getitem__(self, key) -> Stock:
        return self._stocks[key]

    def total(self) -> float:
        raise NotImplementedError()


class Timeseries:
    def __init__(self, size: int = 100, keep: int = 30) -> None:
        self._size = size
        self._keep = keep
        self._watermark = -1
        self._timestamp = -1
        self._data = {'price': np.zeros(size, dtype=float),
                      'quantity': np.zeros(size, dtype=float)}

    def add(self, key: str) -> None:
        self._data[key] = np.zeros(self._size, dtype=float)

    def erase(self) -> None:
        for arr in self._data.values():
            arr[:] = 0

    def __getitem__(self, key) -> np.ndarray:
        return self._data[key]

    def __len__(self) -> int:
        return self._size

    def __iadd__(self, msg: Msg) -> 'Timeseries':
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
        for arr in self._data.values():
            # bring forward the given number of back items
            arr[:self._keep] = arr[-self._keep:]
            arr[self._keep:] = 0  # then make zero the remaining

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}('
                f'columns={[key for key in self._data]}, '
                f'length={len(self)}, '
                f'watermark={self._watermark}'
                f')')
