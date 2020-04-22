import pytest

from backtest.data import Order


@pytest.mark.parametrize('input, expected', [
    (('AAA', 'KOSPI', 1000, 10, 10, 1, 0, 12345), 10011),
    (('AAA', 'KOSPI', 1000, -10, 10, 1, 0, 12345), -10011),
])
def test_total_cost(input, expected):
    sut = Order(*input)
    assert sut.total_cost() == expected
