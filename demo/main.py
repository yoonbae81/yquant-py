import backtest

if __name__ == '__main__':
    market = 'korea'
    strategy = 'dummy'
    initial_cash = 1_000_000
    ticks_dir = 'ticks'
    ledger_dir = 'ledger'

    backtest.run(market,
                 strategy,
                 ticks_dir,
                 ledger_dir,
                 initial_cash)
