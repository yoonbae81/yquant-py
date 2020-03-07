import logging
from collections import defaultdict
from types import SimpleNamespace

import backtester
from backtester.data import Dataset, Order, Tick

config = {
    'initial_cash': 100_000,
    'ticks_dir': 'ticks/',
    'ledger_dir': 'ledger/',
    'threshold': 5,
    'market': ['KOSPI', 'KOSDAQ'],
}


def calc_quantity_to_buy(initial_cash, current_cash, holding, dataset):
    return 1


def calc_quantity_to_sell(holding, dataset):
    return holding


def calc_stoploss(stoploss, dataset):
    return stoploss


strategy = SimpleNamespace(
    calc_quantity_to_buy=calc_quantity_to_buy,
    calc_quantity_to_sell=calc_quantity_to_sell,
    calc_stoploss=calc_stoploss)

if __name__ == '__main__':
    backtester.run(config, strategy)
