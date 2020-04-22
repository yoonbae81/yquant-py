import json
import pytest

import backtest.broker as sut


@pytest.fixture(scope='session')
def rules():
    yield json.load(open('demo/market/rules.json'))


@pytest.mark.parametrize('input, expected', [
    ((10000, 10), 15),
    ((10000, -10), 15),
    ((10000, 10), 15),
    ((10000, -10), 15),
])
def test_commission(input, expected, rules):
    actual = sut._calc_commission(*input, rules['KOSPI']['commission'])

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ((10000, 10), 0),
    ((10000, -10), 250),
])
def test_tax(input, expected, rules):
    actual = sut._calc_tax(*input, rules['KOSPI']['tax'])

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
def test_get_unit_price_KOSPI(input, expected, rules):
    market = 'KOSPI'
    actual = sut._get_price_unit(input, rules[market]['price_units'])

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    (999, 1),
    (1000, 5),
    (4999, 5),
    (5000, 10),
    (10000, 50),
    (50000, 100),
    (100000, 100),
    (499999, 100),
    (500000, 100),
])
def test_get_unit_price_KOSDAQ(input, expected, rules):
    market = 'KOSDAQ'
    actual = sut._get_price_unit(input, rules[market]['price_units'])

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ((100, 10), range(95, 105 + 1, 1)),
    ((10000, 10), range(9750, 10250 + 1, 50)),
])
def test_simulate_market_price(input, expected, rules):
    market = 'KOSDAQ'
    actual = sut._simulate_market_price(*input, rules[market]['price_units'])

    assert actual in expected
