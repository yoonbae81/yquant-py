from multiprocessing import Pipe
from os import remove
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from backtest.fetcher import Fetcher


def test_parse():
    line = 'AAAAA 10000 10 1234512345'
    msg = Fetcher._parse(line)
    assert msg.symbol == 'AAAAA'
    assert msg.price == 10000
    assert msg.quantity == 10
    assert msg.timestamp == 1234512345


@pytest.mark.parametrize('input', [
    ('\n'),
    ('WRONG'),
    ('WRONG WRONG'),
    ('WRONG, 100, 10, 12345'),  # no comma
    ('WRONG 100 10 1234512345.0'),  # wrong timestamp format
    ('WRONG 100 10 1234512345 MORE'),
])
def test_parse_error(input):
    with pytest.raises(ValueError):
        Fetcher._parse(input)


@pytest.fixture(scope='session')
def tick_file():
    # with TemporaryDirectory() as temp_dir:
    # with NamedTemporaryFile('wt', dir=temp_dir, delete=False) as file1:
    with NamedTemporaryFile('wt', delete=False) as file:
        file.write('AAAAA 1000 1 1000000001\n')
        file.write('AAAAA 1100 2 1000000002\n')
        file.write('AAAAA 1100 3 1000000003\n')
        file.write('BBBBB 3000 1 1000000004\n')

    yield Path(file.name)
    remove(file.name)


def test_get_tick_file(tick_file):
    sut = Fetcher(tick_file)
    actual = sut._get_files()
    assert actual == [tick_file]


def test_fetch(tick_file):
    sut = Fetcher(tick_file)
    reader, sut.output = Pipe()

    sut.start()
    sut.join()

    assert reader.recv().symbol == "AAAAA"
    assert reader.recv().symbol == "AAAAA"
    assert reader.recv().symbol == "AAAAA"
    assert reader.recv().symbol == "BBBBB"
