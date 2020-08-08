from backtest.data import Positions, Stock


def test_stock():
    sut = Stock()

    assert sut.price == 0
    assert sut.quantity == 0

    # sut.quantity


def test_total():
    sut = Positions()

    # sut['A']
