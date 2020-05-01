from backtest.analyzer import Analyzer as Sut


def test_init():
    sut = Sut('dummy')
    assert sut
