import pytest

import demo.market.korea as sut


@pytest.mark.parametrize('input, expected', [
    ((10000, 10), 15),
    ((10000, -10), 15),
    ((10000, 10), 15),
    ((10000, -10), 15),
])
def test_commission(input, expected):
    actual = sut.calc_commission('kospi', *input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    ((10000, 10), 0),
    ((10000, -10), 250),
])
def test_tax(input, expected):
    actual = sut.calc_tax('kospi', *input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    (('kospi', 999), 1),
    (('kospi', 1000), 5),
    (('kospi', 4999), 5),
    (('kospi', 5000), 10),
    (('kospi', 10000), 50),
    (('kospi', 50000), 100),
    (('kospi', 100000), 500),
    (('kospi', 499999), 500),
    (('kospi', 500000), 1000),
    (('kosdaq', 999), 1),
    (('kosdaq', 1000), 5),
    (('kosdaq', 4999), 5),
    (('kosdaq', 5000), 10),
    (('kosdaq', 10000), 50),
    (('kosdaq', 50000), 100),
    (('kosdaq', 100000), 100),
    (('kosdaq', 499999), 100),
    (('kosdaq', 500000), 100),
])
def test_get_unit_price(input, expected):
    actual = sut.get_unit(*input)

    assert actual == expected


@pytest.mark.parametrize('input, expected', [
    (('kosdaq', 100, 10), range(95, 105 + 1, 1)),
    (('kosdaq', 10000, 10), range(9750, 10250 + 1, 50)),
])
def test_simulate_price(input, expected):
    actual = sut.simulate_price(*input)

    assert actual in expected
