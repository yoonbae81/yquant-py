import pytest
from multiprocessing import Value

from backtest.data import Asset as Sut


def test_ctor():
    cash = Value('d', 1000)

    sut = Sut(cash)
    assert sut.current_cash == 1000

    cash.value = 900
    assert sut.current_cash == 900
