import numpy as np
import pytest

from backtest.data import Msg, Timeseries


def test_size():
    size = 10
    sut = Timeseries(size)

    assert len(sut) == size


def test_add():
    sut = Timeseries()

    sut += Msg('SYMBOL', price=1000, quantity=10, timestamp=1)
    assert sut['price'][0] == 1000
    assert sut['quantity'][0] == 10

    sut += Msg('SYMBOL', price=2000, quantity=20, timestamp=2)
    assert sut['price'][1] == 2000
    assert sut['quantity'][1] == 20

    assert sut['price'][2] == 0
    assert sut['price'][2] == 0


def test_add_same_timestamp():
    sut = Timeseries()

    sut += Msg('SYMBOL', price=1000, quantity=10, timestamp=1)
    sut += Msg('SYMBOL', price=1000, quantity=10, timestamp=1)

    assert sut['price'][0] == 1000  # override price
    assert sut['quantity'][0] == 20  # add quantity


def test_overflow():
    size = 10
    keep = 3
    sut = Timeseries(size, keep)

    for i in range(1, size + keep):
        sut += Msg('SYMBOL', price=i, quantity=i, timestamp=i)

    assert sut['price'][0] == 8  # keep value
    assert sut['price'][1] == 9  # keep value
    assert sut['price'][2] == 10  # keep value
    assert sut['price'][3] == 11  # new value

    assert sut['quantity'][0] == 8  # keep value
    assert sut['quantity'][1] == 9  # keep value
    assert sut['quantity'][2] == 10  # keep value
    assert sut['quantity'][3] == 11  # new value


def test_add_timeseries():
    sut = Timeseries()

    with pytest.raises(KeyError):
        sut['new']

    sut.add('new')  # add new time series data
    assert type(sut['new']) == np.ndarray
    assert len(sut['new']) == sut._size
