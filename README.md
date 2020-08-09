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
  - [Usage](#usage)
  - [Support](#support)
  - [Contributing](#contributing)
  - [Testing](#testing)


## Installation

    $ pip install backtest


## Preparation 

Fetching symbols of KOSPI and KOSDAQ exchanges:


    $ python -m backtest.utils.symbols_krx symbols.json
    Fetched 2,820 symbols
    Saved in symbols.json


## Usage

The following will execute the backtest after loading configuration file, `config.json` in same directory.

    python -m backtest

Sample content of `config.json`
```json
{
  "cash": 1000000,
  "ticks": "./ticks",
  "ledger": "./ledger",
  "symbols": "./symbols.json",
  "strategy": "strategy",
  "exchange": "backtest.exchanges.korea_exchange"
}
```


## Support

Please [open an issue](https://github.com/yoonbae82/backtest/issues/new) for support.


## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/yoonbae/backtest/compare/).


## Testing

Test codes are prepared in _tests/_ based on [PyTest](https://docs.pytest.org/en/latest/) framework.

