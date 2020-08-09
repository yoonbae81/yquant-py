import pytest


@pytest.mark.parametrize('symbol, record', [
    ('005930', {'market': 'KOSPI',
                'name': '삼성전자'}),
    ('091990', {'market': 'KOSDAQ',
                'name': '셀트리온헬스케어'}),
])
def test_record(symbols, symbol, record):
    assert symbols[symbol] == record


def test_count(symbols):
    assert len(symbols) > 2500
