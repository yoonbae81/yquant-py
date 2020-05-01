import json
import numbers
from contextlib import nullcontext as does_not_raise
from datetime import datetime
from multiprocessing.connection import Pipe
from pathlib import Path

import pytest

from backtest.data import Msg
from backtest.ledger import Ledger as Sut


def test_init(tmp_path):
    sut = Sut(tmp_path)
    assert sut


def test_open_file(tmp_path):
    Sut(tmp_path)
    today = f'{datetime.now():%Y%m%d}'
    assert tmp_path.glob(f'{today}*.json')


@pytest.mark.parametrize('input, expected', [
    ({'cash': 10}, does_not_raise()),
    ({'cash': 'AAA'}, pytest.raises(TypeError)),
    ({'cash': -1}, pytest.raises(ArithmeticError)),
])
def test_cash(tmp_path, input, expected):
    sut = Sut(tmp_path)
    with expected:
        sut._handler_cash(Msg('CASH', **input))
    sut._file.close()

    if isinstance(input['cash'], numbers.Number) and input['cash'] > 0:
        text = Path(sut._file.name).read_text()
        assert json.loads(text)['cash'] == input['cash']


def test_quit(tmp_path):
    sut = Sut(tmp_path)
    sut.input, router = Pipe(duplex=False)

    sut.start()
    router.send(Msg('QUIT'))
    sut.join()

    assert True
