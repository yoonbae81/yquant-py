import pytest

from backtest.data import Filled


@pytest.mark.parametrize('input, expected', [
    (('AAA', 'KOSPI', 1000, 10, 10, 1, 0, 12345), 10011),
    (('AAA', 'KOSPI', 1000, -10, 10, 1, 0, 12345), -10011),
])
def test_total_cost(input, expected):
    sut = Filled(*input)
    assert sut.total_cost() == expected
