import pytest

import backtest.market.korea as sut


@pytest.mark.parametrize('input, expected', [
    ({'exchange': 'kospi', 'price': 999}, 1),
    ({'exchange': 'kospi', 'price': 1_000}, 5),
    ({'exchange': 'kospi', 'price': 4_999}, 5),
    ({'exchange': 'kospi', 'price': 5_000}, 10),
    ({'exchange': 'kospi', 'price': 10_000}, 50),
    ({'exchange': 'kospi', 'price': 50_000}, 100),
    ({'exchange': 'kospi', 'price': 100_000}, 500),
    ({'exchange': 'kospi', 'price': 499_999}, 500),
    ({'exchange': 'kospi', 'price': 500_000}, 1000),
    ({'exchange': 'kosdaq', 'price': 999}, 1),
    ({'exchange': 'kosdaq', 'price': 1_000}, 5),
    ({'exchange': 'kosdaq', 'price': 4_999}, 5),
    ({'exchange': 'kosdaq', 'price': 5_000}, 10),
    ({'exchange': 'kosdaq', 'price': 10_000}, 50),
    ({'exchange': 'kosdaq', 'price': 50_000}, 100),
    ({'exchange': 'kosdaq', 'price': 100_000}, 100),
    ({'exchange': 'kosdaq', 'price': 499_999}, 100),
    ({'exchange': 'kosdaq', 'price': 500_000}, 100),
])
def test_get_unit_price(input, expected):
    actual = sut.get_unit(**input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ({'exchange': 'kospi', 'price': 10000, 'quantity': 10}, 15),
    ({'exchange': 'kospi', 'price': 10000, 'quantity': -10}, 15),
])
def test_commission(input, expected):
    actual = sut.calc_commission(**input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ({'exchange': 'kospi', 'price': 10000, 'quantity': 10}, 0),
    ({'exchange': 'kospi', 'price': 10000, 'quantity': -10}, 250),
])
def test_tax(input, expected):
    actual = sut.calc_tax(**input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ({'exchange':'kosdaq', 'price':100, 'quantity':10}, range(95, 105 + 1, 1)),
    ({'exchange':'kosdaq', 'price':10000, 'quantity':10}, range(9750, 10250+ 1, 50)),
])
def test_simulate_price(input, expected):
    actual = sut.simulate_price(**input)

    assert actual in expected
