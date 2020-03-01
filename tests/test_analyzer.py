import numpy as np

from backtester.analyzer import Ticks
from backtester.fetcher import Tick


def test_ticks_add():
    sut = Ticks()

    sut.add(Tick('A', 1000, 10, 1))
    assert sut.prices[0] == 1000
    assert sut.quantities[0] == 10

    sut.add(Tick('A', 2000, 20, 2))
    assert sut.prices[1] == 2000
    assert sut.quantities[1] == 20

    assert sut.prices[2] == 0
    assert sut.prices[2] == 0


def test_ticks_add_same_timestamp():
    sut = Ticks()

    sut.add(Tick('A', 1000, 10, 1))
    sut.add(Tick('A', 1000, 10, 1))

    assert sut.prices[0] == 1000  # override price
    assert sut.quantities[0] == 20  # add quantity


def test_ticks_overflow():
    size = 10
    keep = 3
    sut = Ticks(size, keep)

    [sut.add(Tick('A', i, i, i))
     for i in range(1, size + keep)]

    assert sut.prices[0] == 8  # keep value
    assert sut.prices[1] == 9  # keep value
    assert sut.prices[2] == 10  # keep value
    assert sut.prices[3] == 11  # new value

    assert sut.quantities[0] == 8  # keep value
    assert sut.quantities[1] == 9  # keep value
    assert sut.quantities[2] == 10  # keep value
    assert sut.quantities[3] == 11  # new value
