import json
from pathlib import Path
from types import SimpleNamespace

import backtest


# could use ta-lib that downloadable from https://www.lfd.uci.edu/~gohlke/pythonlibs/
def calc_strength(stock):
    return 0


def calc_stoploss(stock):
    return 1


def calc_quantity(signal, cash, quantity_dict):
    return 100


strategy = SimpleNamespace(
    calc_strength=calc_strength,
    calc_stoploss=calc_stoploss,
    calc_quantity=calc_quantity)


if __name__ == '__main__':
    files = {'symbols': 'market/symbols.json',
             'rules': 'market/rules.json', }

    market = {}
    for key, path in files.items():
        with Path(__file__).parent.joinpath(path).open(encoding='utf-8') as f:
            market[key] = json.load(f)

    backtest.run(market, strategy, 'ticks/', 'ledger/', initial_cash=1_000_000)
