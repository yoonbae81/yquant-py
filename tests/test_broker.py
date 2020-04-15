import json
import pytest

import backtester.broker as sut


@pytest.fixture(scope='session')
def config():
    yield {'market': json.load(open('../config/market.json'))}


@pytest.mark.parametrize('input, expected', [
    (('KOSPI', 10000, 10), 15),
    (('KOSPI', 10000, -10), 15),
    (('KOSDAQ', 10000, 10), 15),
    (('KOSDAQ', 10000, -10), 15),
])
def test_commission(config, input, expected):
    actual = sut._calc_commission(config, *input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    (('KOSPI', 10000, 10), 0),
    (('KOSPI', 10000, -10), 250),
])
def test_tax(config, input, expected):
    actual = sut._calc_tax(config, *input)

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
def test_get_unit_price_KOSPI(config, input, expected):
    market = 'KOSPI'
    actual = sut._get_price_unit(config, market, input)

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
def test_get_unit_price_KOSDAQ(config, input, expected):
    market = 'KOSDAQ'
    actual = sut._get_price_unit(config, market, input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ((100, 10), range(95, 105 + 1, 1)),
    ((10000, 10), range(9750, 10250 + 1, 50)),
])
def test_simulate_market_price(config, input, expected):
    config['broker'] = {'slippage_stdev': 0.7}
    market = 'KOSPI'
    actual = sut._simulate_market_price(config, market, *input)

    assert actual in expected
