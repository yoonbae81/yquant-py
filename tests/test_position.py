from backtest.data import Position as Sut


def test_new():
    sut = Sut(1000, 1)

    assert sut.price == 1000
    assert sut.quantity == 1


def test_buy():
    sut = Sut(1000, 1)
    sut.add(2000, 1)

    assert sut.price == 1500
    assert sut.quantity == 2


def test_sell():
    sut = Sut(1000, 2)
    sut.add(2000, -1)

    assert sut.price == 1000
    assert sut.quantity == 1


def test_sell_all():
    sut = Sut(1000, 2)
    sut.add(2000, -2)

    assert sut.price == 1000
    assert sut.quantity == 0
