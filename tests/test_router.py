from unittest.mock import Mock, patch

import pytest

from backtest.analyzer import Analyzer
from backtest.broker import Broker
from backtest.data import Msg
from backtest.fetcher import Fetcher
from backtest.ledger import Ledger
from backtest.router import Router as Sut


@pytest.fixture(scope='function')
def sut():
    yield Sut()


def test_init(sut):
    assert sut


@pytest.fixture(scope='function')
def nodes():
    output = {
        'Fetcher': Mock(spec=Fetcher),
        'Analyzer1': Mock(spec=Analyzer),
        'Analyzer2': Mock(spec=Analyzer),
        'Analyzer3': Mock(spec=Analyzer),
        'Broker': Mock(spec=Broker),
        'Ledger': Mock(spec=Ledger),
    }

    yield output


def test_connect(sut, nodes):
    [sut.connect(node) for node in nodes.values()]
    sut.connect(sut)  # Router will ignore connection to router


def test_connect_error(sut):
    with pytest.raises(TypeError):
        sut.connect('Unknown Node')


def test_get_analyzers(sut, nodes):
    [sut.connect(node) for node in nodes.values()]

    assert sut._get_analyzer('A') == sut._to_analyzers[0]
    assert sut._get_analyzer('B') == sut._to_analyzers[1]
    assert sut._get_analyzer('C') == sut._to_analyzers[2]
    assert sut._get_analyzer('A') == sut._to_analyzers[0]


@pytest.mark.parametrize('msg, target', [
    (Msg('TICK', symbol='A'), 'Analyzer1'),
    (Msg('ORDER'), 'Broker'),
    (Msg('CASH'), 'Ledger'),
    (Msg('FILL'), 'Ledger'),
    (Msg('QUANTITY', symbol='A'), 'Analyzer1'),
])
def test_handler_msg(sut, nodes, msg, target):
    [sut.connect(node) for node in nodes.values()]
    sut.handle(msg)

    assert nodes[target].input.recv() == msg


def test_handler_eof(sut, nodes):
    [sut.connect(node) for node in nodes.values()]
    sut.handle(Msg('EOF'))

    for t in ['Analyzer1', 'Analyzer2', 'Analyzer3']:
        assert nodes[t].input.recv() == Msg('RESET')


def test_handler_quit(sut, nodes):
    del nodes['Fetcher']
    [sut.connect(node) for node in nodes.values()]

    msg = Msg('QUIT')
    sut.handle(msg)

    for t in nodes:
        assert nodes[t].input.recv() == msg


def test_handler_unknown(sut):
    result = sut.handle(Msg('_UNKNOWN_'))

    assert not result
