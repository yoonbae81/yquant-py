from multiprocessing import cpu_count
from types import SimpleNamespace

import backtester

CONFIG = {
    'initial_cash': 100_000,
    'symbols_json': 'symbols.json',
    'ticks_dir': 'ticks/',
    'ledger_dir': 'ledger/',
    'slippage_stdev': 0.7,
    'num_analyzer': max(1, cpu_count() - 1),
}


def calc_quantity_to_buy(initial_cash, current_cash, holding, dataset):
    return 1


def calc_quantity_to_sell(holding, dataset):
    return 1


def calc_stoploss(stoploss, dataset):
    return stoploss


strategy = SimpleNamespace(
    calc_quantity_to_buy=calc_quantity_to_buy,
    calc_quantity_to_sell=calc_quantity_to_sell,
    calc_stoploss=calc_stoploss)

if __name__ == '__main__':
    backtester.run(CONFIG, strategy)
