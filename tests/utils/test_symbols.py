import pytest


@pytest.mark.parametrize('symbol, record', [
    ('005930', {'exchange': 'kospi',
                'name': '삼성전자'}),
    ('091990', {'exchange': 'kosdaq',
                'name': '셀트리온헬스케어'}),
])
def test_record(symbols, symbol, record):
    assert symbols[symbol] == record


def test_count(symbols):
    assert len(symbols) > 2500
