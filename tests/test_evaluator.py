import pytest

from backtest.evaluator import evaluate


def test_dummmy():
    actual = evaluate([], 'file', 'benchmark')

    assert actual['profit'] == 99