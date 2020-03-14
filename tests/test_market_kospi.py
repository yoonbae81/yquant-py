import pytest

from backtester.data import Order
import backtester.market.kospi as sut


@pytest.mark.parametrize('input, expected', [
    (Order('A', 10000, 10, 1), 15),
    (Order('A', 10000, -10, 1), 15),
])
def test_commission(input, expected):
    actual = sut.calc_commission(input)
    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    (Order('A', 10000, 10, 1), 0),
    (Order('A', 10000, -10, 1), 250),
])
def test_tax(input, expected):
    actual = sut.calc_tax(input)
    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    (999, 1),
    (1000, 5),
    (4999, 5),
    (5000, 10),
    (10000, 50),
    (50000, 100),
    (100000, 500),
    (499999, 500),
    (500000, 1000),
])
def test_get_unit_price(input, expected):
    actual = sut._get_unit_price(input)
    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    (Order('A', 100, 10, 1), range(95, 105 + 1, 1)),
    (Order('A', 10000, 10, 1), range(9750, 10250 + 1, 50)),
])
def test_simulate_market_price(input, expected):
    actual = sut.simulate_market_price(input, 0.7)
    assert actual in expected
