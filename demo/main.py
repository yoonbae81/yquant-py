from pathlib import Path

import backtest
from demo.market import korea as market
from demo.strategy import dummy as strategy

if __name__ == '__main__':
    market = 'korea'
    strategy = 'dummy'
    initial_cash = 1_000_000
    ticks_dir = Path('ticks/')
    ledger_dir = Path('ledger/')

    backtest.run(market,
                 strategy,
                 ticks_dir,
                 ledger_dir,
                 initial_cash)
