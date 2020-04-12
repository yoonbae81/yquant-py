import pytest

from backtester.data import Filled


@pytest.mark.parametrize('input, expected', [
    (('AAA', 10, 1000, 10, 1, 0, 12345), 10011),
    (('AAA', -10, 1000, 10, 1, 0, 12345), -10011),
])
def test_total_cost(input, expected):
    sut = Filled(*input)
    assert sut.total_cost() == expected
