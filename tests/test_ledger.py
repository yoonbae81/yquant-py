import json
from contextlib import nullcontext as does_not_raise
from datetime import datetime
from io import StringIO
from unittest.mock import patch

import pytest

from backtest.data import Msg
from backtest.ledger import Ledger as Sut


def test_init(tmp_path):
    sut = Sut(tmp_path)
    assert sut


def test_create_file(tmp_path):
    Sut(tmp_path)
    today = f'{datetime.now():%Y%m%d}'
    assert tmp_path.glob(f'{today}*.json')


def test_handler_quit(tmp_path):
    sut = Sut(tmp_path)

    with patch.object(sut, 'input', create=True) as mock_input:
        mock_input.recv.return_value = Msg('QUIT')
        sut.start()
        sut.join()

    assert True


@pytest.mark.parametrize('input, expected', [
    (Msg('CASH', cash=1000), '{"cash": 1000}\n'),
    (Msg('CASH', cash=0), '{"cash": 0}\n'),
])
def test_handler_cash_ok(tmp_path, input, expected):
    sut = Sut(tmp_path)
    with patch.object(sut, '_file', new_callable=StringIO) as mock_file:
        sut._handler_cash(input)
        assert mock_file.getvalue() == expected


@pytest.mark.parametrize('input, expected', [
    ({'cash': 10}, does_not_raise()),
    ({'cash': 0}, does_not_raise()),
    ({'cash': -1}, pytest.raises(ArithmeticError)),
    ({'cash': 'STRING_IS_NOT_ACCEPTABLE'}, pytest.raises(TypeError)),
])
def test_handler_cash_error(tmp_path, input, expected):
    sut = Sut(tmp_path)

    with expected:
        sut._handler_cash(Msg('CASH', **input))


@pytest.mark.parametrize('input', [
    Msg('ORDER', symbol='015760', quantity=1, price=30000)
])
def test_handler_order(tmp_path, input):
    sut = Sut(tmp_path)
    with patch.object(sut, '_file', new_callable=StringIO) as mock_file:
        sut._handler_fill(input)
        output = json.loads(mock_file.getvalue())

    assert output['symbol'] == input.symbol
    assert output['quantity'] == input.quantity
    assert output['price'] == input.price
