import pytest

from backtest.broker import Broker as sut


@pytest.mark.parametrize('input, expected', [
    ({'price': 1000, 'quantity': 1, 'commission': 100, 'tax': 10}, 1110),
    ({'price': 1000, 'quantity': -1, 'commission': 100, 'tax': 10}, -1110),
])
def test_calc_total_cost(input, expected):
    actual = sut._calc_total_cost(**input)

    assert actual == expected

