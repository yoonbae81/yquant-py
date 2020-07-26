import pytest

import backtest.exchanges.kosdaq as sut


@pytest.mark.parametrize('input, expected', [
    ({'price': 10000, 'quantity': 10}, 15),
    ({'price': 10000, 'quantity': -10}, 15),
])
def test_commission(input, expected):
    actual = sut.calc_commission(**input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ({'price': 10000, 'quantity': 10}, 0),
    ({'price': 10000, 'quantity': -10}, 250),
])
def test_tax(input, expected):
    actual = sut.calc_tax(**input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    (999, 1),
    (1_000, 5),
    (4_999, 5),
    (5_000, 10),
    (10_000, 50),
    (50_000, 100),
    (100_000, 100),
    (499_999, 100),
    (500_000, 100),
])
def test_get_unit_price(input, expected):
    actual = sut.get_unit(input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ({'price': 100, 'quantity': 10}, range(95, 105 + 1, 1)),
    ({'price': 10000, 'quantity': 10}, range(9750, 10250 + 1, 50)),
])
def test_simulate_price(input, expected):
    actual = sut.simulate_price(**input)

    assert actual in expected
