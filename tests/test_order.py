import pytest

from backtest.data import Order as Sut

RATES = {
    'tax': {
        'buy': 0,
        'sell': 0.0025
    },
    'commission': {
        'buy': 0.00015,
        'sell': 0.00015
    }
}


@pytest.mark.parametrize('input, expected', [
    ({'price': 100_000, 'quantity': 10, 'rates': RATES}, 150),
    ({'price': 100_000, 'quantity': -10, 'rates': RATES}, 150),
])
def test_commission(input, expected):
    sut = Sut("A", **input)

    assert sut.commission == expected


@pytest.mark.parametrize('input, expected', [
    ({'price': 100_000, 'quantity': 10, 'rates': RATES}, 0),
    ({'price': 100_000, 'quantity': -10, 'rates': RATES}, 2500),
])
def test_tax(input, expected):
    sut = Sut("A", **input)

    assert sut.tax == expected


@pytest.mark.parametrize('input, expected', [
    ({'price': 100_000, 'quantity': 10, 'rates': RATES}, 1_000_150),
    ({'price': 100_000, 'quantity': -10, 'rates': RATES}, -1_002_650),
])
def test_total_cost(input, expected):
    sut = Sut("A", **input)

    assert sut.total_cost == expected
