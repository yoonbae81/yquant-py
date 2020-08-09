import pytest

from backtest.exchanges.korea_exchange import Trade, KoreaExchange


@pytest.fixture(scope='session')
def exchange(symbols) -> KoreaExchange:
    slippage_mean: float = 0.5
    slippage_stdev: float = 0.7

    yield KoreaExchange(symbols, slippage_mean, slippage_stdev)


@pytest.mark.parametrize('symbol, expected', [
    ('005930', 'KOSPI'),
    ('091990', 'KOSDAQ'),
    ('UNKNOWN', 'KOSDAQ')
])
def test_get_market(exchange, symbol, expected):
    actual = exchange._get_market(symbol)
    assert actual == expected


@pytest.mark.parametrize('price, expected', [
    (999, 1),
    (1_000, 5),
    (4_999, 5),
    (5_000, 10),
    (10_000, 50),
    (50_000, 100),
    (100_000, 500),
    (499_999, 500),
    (500_000, 1000),
])
def test_get_price_unit_kospi(exchange, price, expected):
    actual = exchange._get_price_unit('KOSPI', price)
    assert actual == expected


@pytest.mark.parametrize('price, expected', [
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
def test_get_price_unit_kosdaq(exchange, price, expected):
    actual = exchange._get_price_unit('KOSDAQ', price)
    assert actual == expected


@pytest.mark.parametrize('price, expected', [
    (100, range(-5, 5 + 1, 1)),
    (1000, range(-250, 250 + 1, 5)),
])
def test_simulate_slippage(exchange, price, expected):
    actual = exchange._simulate_slippage('KOSPI', Trade.BUY, price)
    assert actual in expected


@pytest.mark.parametrize('input, expected', [
    ({'trade': Trade.BUY, 'price': 100_000, 'quantity': 10}, 0),
    ({'trade': Trade.SELL, 'price': 100_000, 'quantity': -10}, 2500),
])
def test_tax(exchange, input, expected):
    actual = exchange._calc_tax(**input)
    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ({'trade': Trade.BUY, 'price': 100_000, 'quantity': 10}, 150),
    ({'trade': Trade.SELL, 'price': 100_000, 'quantity': -10}, 150),
])
def test_commission(exchange, input, expected):
    actual = exchange._calc_commission(**input)
    assert actual == expected

