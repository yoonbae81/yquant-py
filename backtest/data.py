from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import DefaultDict, Optional

import numpy as np


@dataclass
class Msg:
    type: str
    symbol: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    strength: Optional[int] = None  # analyzer
    cash: Optional[float] = None  # broker
    commission: Optional[float] = None  # broker, ledge
    tax: Optional[float] = None  # broker, ledge
    slippage: Optional[float] = None  # broker, ledge
    timestamp: Optional[int] = None

    def __repr__(self):
        l = []
        for k, v in asdict(self).items():
            if v:
                v = f"'{v}'" if isinstance(v, str) else v
                l.append(f'{k}={v}')

        return (f'{self.__class__.__name__}('
                + ', '.join(l)
                + f')')


@dataclass
class Stock:
    price: float = 0
    quantity: float = 0


class Positions:
    def __init__(self) -> None:
        self._stocks: DefaultDict[str, Stock] = defaultdict(Stock)

    def __getitem__(self, key) -> Stock:
        return self._stocks[key]

    def total(self) -> float:
        raise NotImplementedError()


class Timeseries:
    def __init__(self, size: int = 100, keep: int = 30) -> None:
        self._size: int = size
        self._keep: int = keep
        self._watermark: int = -1
        self._timestamp: int = None
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
