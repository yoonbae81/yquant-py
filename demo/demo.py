import json
from pathlib import Path
from types import SimpleNamespace

import backtest


# could use ta-lib that downloadable from https://www.lfd.uci.edu/~gohlke/pythonlibs/
def calc_strength(stock) -> int:
    return 2


def calc_stoploss(stock) -> float:
    return 1


def calc_quantity(signal, cash, quantity_dict) -> float:
    return 100


if __name__ == '__main__':
    files = {'symbols': 'market/symbols.json',
             'rules': 'market/rules.json', }

    market = {}
    for key, path in files.items():
        with Path(__file__).parent.joinpath(path).open(encoding='utf-8') as f:
            market[key] = json.load(f)

    # backtest.run(market, strategy, 'ticks/', 'ledger/', initial_cash=1_000_000)

    initial_cash = 1_000_000
    ticks_dir = Path('ticks/')
    ledger_dir = Path('ledger/')
    symbols = json.load(Path('market/symbols.json').open(encoding='utf-8'))
    rules = json.load(Path('market/rules.json').open(encoding='utf-8'))
    strategy = SimpleNamespace(
        calc_strength=calc_strength,
        calc_stoploss=calc_stoploss,
        calc_quantity=calc_quantity)

    backtest.run(strategy, ticks_dir, ledger_dir, symbols, rules, initial_cash)
