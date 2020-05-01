from backtest.router import Router as Sut


def test_init():
    sut = Sut()
    assert sut
