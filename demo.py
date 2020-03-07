import logging
from collections import defaultdict

import backtester
from backtester.data import History, Order, Tick

config = {
    'cash': 100_000,
    'ticks_dir': 'ticks/',
    'ledger_dir': 'ledger/',
    'threshold': 5,
    'market': ['KOSPI', 'KOSDAQ'],
}


def calc_quantity(cash, quantity, history):
    return 1


def calc_stoploss(history: History):
    return 1


def strategy(cash: float, quantity: float, stoploss: float, history: History):
    quantity = calc_quantity(cash, quantity, history)
    stoploss = calc_stoploss(history)
    return quantity, stoploss


if __name__ == '__main__':
    backtester.run(config, strategy)
