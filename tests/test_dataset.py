from backtester.data import Dataset
from backtester.fetcher import Tick


def test_size():
    size = 10
    sut = Dataset(size)
    assert len(sut) == size


def test_add():
    sut = Dataset()

    sut += Tick('A', 1000, 10, 1)
    assert sut['price'][0] == 1000
    assert sut['volume'][0] == 10

    sut += Tick('A', 2000, 20, 2)
    assert sut['price'][1] == 2000
    assert sut['volume'][1] == 20

    assert sut['price'][2] == 0
    assert sut['price'][2] == 0


def test_add_same_timestamp():
    sut = Dataset()

    sut += Tick('A', 1000, 10, 1)
    sut += Tick('A', 1000, 10, 1)

    assert sut['price'][0] == 1000  # override price
    assert sut['volume'][0] == 20  # add quantity


def test_overflow():
    size = 10
    keep = 3
    sut = Dataset(size, keep)

    for i in range(1, size + keep):
        sut += Tick('A', i, i, i)

    assert sut['price'][0] == 8  # keep value
    assert sut['price'][1] == 9  # keep value
    assert sut['price'][2] == 10  # keep value
    assert sut['price'][3] == 11  # new value

    assert sut['volume'][0] == 8  # keep value
    assert sut['volume'][1] == 9  # keep value
    assert sut['volume'][2] == 10  # keep value
    assert sut['volume'][3] == 11  # new value