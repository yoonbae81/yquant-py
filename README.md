# Backtest

[![Python version](https://img.shields.io/pypi/pyversions/backtest.svg)](https://pypi.org/project/backtest/)
[![PyPI version](https://img.shields.io/pypi/v/backtest.svg)](https://pypi.org/project/backtest/)
[![Test](https://github.com/yoonbae81/backtest/workflows/test/badge.svg)](https://github.com/yoonbae81/backtest/actions?query=workflow%3Atest)
[![Build](https://github.com/yoonbae81/backtest/workflows/build/badge.svg)](https://github.com/yoonbae81/backtest/actions?query=workflow%3Abuild)
[![Coverage](https://codecov.io/gh/yoonbae81/backtest/graph/badge.svg)](http://codecov.io/gh/yoonbae81/backtest)
[![Docs](https://readthedocs.org/projects/backtest/badge/?version=latest)](https://backtest.readthedocs.io/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A [backtest](https://en.wikipedia.org/wiki/Backtesting) engine for developing [algorithmic trading](https://en.wikipedia.org/wiki/Algorithmic_trading) strategy.


## Table of Contents

- [Backtest](#backtest)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Preparation](#preparation)
  - [Usage](#usage)
  - [Support](#support)
  - [Contributing](#contributing)
  - [Testing](#testing)


## Installation

    $ pip install backtest


## Preparation 

Fetching symbols of KOSPI and KOSDAQ exchanges:


    $ python -m backtest.symbols.korea_symbols.json
    Fetched 2,820 symbols
    Saved in symbols.json


## Usage

The following will execute the backtest with the symbols file, `symbols.json` in the same directory.

    $ python momentum.py -s symbols.json

Sample output as follows:
```
21:00:43,051 DEBUG    fetcher.py  Initialized
21:00:43,052 DEBUG    analyzer.py Initialized Analyzer1
21:00:43,052 DEBUG    analyzer.py Initialized Analyzer2
21:00:43,052 DEBUG    broker.py   Initialized
21:00:43,053 DEBUG    ledger.py   Preparing file: ledger/043.jsonl
21:00:43,053 DEBUG    router.py   Initialized
21:00:43,054 DEBUG    router.py   Connected to Ledger
21:00:43,055 DEBUG    router.py   Connected to Broker
21:00:43,055 DEBUG    router.py   Connected to Analyzer1
21:00:43,055 DEBUG    router.py   Connected to Analyzer2
21:00:43,056 DEBUG    router.py   Connected to Fetcher
21:00:43,057 DEBUG    router.py   Starting...
21:00:43,057 DEBUG    broker.py   Starting...
21:00:43,082 DEBUG    fetcher.py  Starting...
21:00:43,126 INFO     fetcher.py  Loading file: ticks/5.txt
21:00:43,545 DEBUG    analyzer.py Analyzer2 starting (pid:8628)
21:00:43,546 DEBUG    analyzer.py Analyzer2 received: Msg', symbol='015760', price=100.0, quantity=2.0, 234512343)
21:00:43,546 DEBUG    analyzer.py Analyzer2 received: Msg', symbol='015760', price=200.0, quantity=2.0, 234512345)
21:00:43,546 DEBUG    broker.py   Received: Msg(type='ORDER', symbol='015760', price=100.0, quantity=100, strength=2, timestamp=1234512343)
...
21:09:14,057 DEBUG    ledger.py   Received: Msg(type='FILL', symbol='015760', price=200.0, quantity=100, strength=2, cash=130669.0, commission=3, timestamp=1234512345)
21:09:14,057 DEBUG    analyzer.py 015760: Position(price=150.0, quantity=200, stoploss=0)
21:09:14,798 INFO     router.py   Elapsed: 1.04 sec (207.18 ms/tick)
```


## Support

Please [open an issue](https://github.com/yoonbae81/backtest/issues/new) for support.


## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/yoonbae/backtest/compare/).


## Testing

Test codes are prepared in _tests/_ based on [PyTest](https://docs.pytest.org/en/latest/) framework.
