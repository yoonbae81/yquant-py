import json
import numbers
from contextlib import nullcontext as does_not_raise
from datetime import datetime
from multiprocessing.connection import Pipe
from pathlib import Path
from unittest import mock

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
    sut.input, router = Pipe(duplex=False)

    sut.start()
    router.send(Msg('QUIT'))
    sut.join()

    assert True


@pytest.mark.parametrize('input, expected', [
    ({'cash': 10}, 10),
])
def test_handler_cash_ok(tmp_path, input, expected):
    sut = Sut(tmp_path)

    sut._file.close()
    text = Path(sut._file.name).read_text()
    assert json.loads(text)['cash'] == expected


@mock.patch('ledger.print')
def test_handler_cash_ok2(tmp_path, mock_print):
    sut = Sut(tmp_path)

    mock_print.assert_called_once_with('{"cash": 10}')


@pytest.mark.parametrize('input, expected', [
    ({'cash': 10}, does_not_raise()),
    ({'cash': -1}, pytest.raises(ArithmeticError)),
    ({'cash': 'STRING_IS_NOT_ACCEPTABLE'}, pytest.raises(TypeError)),
])
def test_handler_cash_error(tmp_path, input, expected):
    sut = Sut(tmp_path)

    with expected:
        sut._handler_cash(Msg('CASH', **input))


def test_handler_order():
    pass
