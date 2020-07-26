import pytest

import backtest.utils.symbols_krx as sut


@pytest.fixture()
def fetched():
    yield sut.run()


@pytest.mark.parametrize('symbol, record', [
    ('005930', {'exchange': 'kospi',
                'name': '삼성전자'}),
    ('091990', {'exchange': 'kosdaq',
                'name': '셀트리온헬스케어'}),
])
def test_record(fetched, symbol, record):
    assert fetched[symbol] == record


def test_count(fetched):
    assert len(fetched) > 2500
