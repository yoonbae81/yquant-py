import pytest

from backtest.broker import Broker as Sut


def test_init():
    sut = Sut('korea', 'dummy', 1000)
    assert sut


@pytest.mark.parametrize('input, expected', [
    ({'price': 1000, 'quantity': 1, 'commission': 100, 'tax': 10}, 1110),
    ({'price': 1000, 'quantity': -1, 'commission': 100, 'tax': 10}, -1110),
])
def test_calc_total_cost(input, expected):
    actual = Sut._calc_total_cost(**input)

    assert actual == expected
