# yQuant

[![Python version](https://img.shields.io/pypi/pyversions/yquant.svg)](https://pypi.org/project/yquant/)
[![PyPI version](https://img.shields.io/pypi/v/yquant.svg)](https://pypi.org/project/yquant/)
[![Test](https://github.com/yoonbae81/yquant/workflows/test/badge.svg)](https://github.com/yoonbae81/yquant/actions?query=workflow%3Atest)
[![Build](https://github.com/yoonbae81/yquant/workflows/build/badge.svg)](https://github.com/yoonbae81/yquant/actions?query=workflow%3Abuild)
[![Coverage](https://codecov.io/gh/yoonbae81/yquant/graph/badge.svg)](http://codecov.io/gh/yoonbae81/yquant)
[![Docs](https://readthedocs.org/projects/yquant/badge/?version=latest)](https://yquant.readthedocs.io/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Table of Contents

- [yQuant](#yquant)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Install Python 3.10 on Ubuntu](#install-python-310-on-ubuntu)
    - [Clone repository from Github](#clone-repository-from-github)
    - [Prepare Python runtime and virutal enviorment](#prepare-python-runtime-and-virutal-enviorment)
  - [Preparation](#preparation)
  - [Usage](#usage)
  - [Support](#support)
  - [Contributing](#contributing)
  - [Testing](#testing)

yQuant is an automatic trading system supporting [backtest](https://en.wikipedia.org/wiki/Backtesting) and trading engine with [algorithmic trading](https://en.wikipedia.org/wiki/Algorithmic_trading) strategy.


For detail on why I've been working on this project and what is the ultimate goal, take a look at the [vision statement](docs/vision.md) and [features](features/README.md).

## Installation

### Install Python 3.10 on Ubuntu

    $ sudo apt-get install software-properties-common
    $ sudo add-apt-repository ppa:deadsnakes/ppa
    $ sudo apt install python3.10 python3.10-venv


### Clone repository from Github

    $ git clone git@github.com:yoonbae81/yquant
    $ cd yquant


### Prepare Python runtime and virutal enviorment

    $ python3.10 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt


## Preparation

Fetching symbols of KOSPI and KOSDAQ exchanges:


    $ python -m backtest.symbols.korea_symbols.json
    Fetched 2,820 symbols
    Saved in symbols.json



## Usage

The following will execute the backtest with the symbols file, `symbols.json` in the same directory.

    $ python backtest.py

Sample output as follows:
```
DEBUG monitor.bootstrap              Initializing...
DEBUG monitor.adapters.file_fetcher  Loading: 1.txt
DEBUG monitor.adapters.file_fetcher  Parsing: 091990 1000 1 1234512340
DEBUG monitor.messages               Created: TickFetched(chains=[], symbol='091990', price=1000.0, qty=1.0, timestamp=1234512340)
DEBUG monitor.facade                 Handler: <lambda> for TickFet hed(chains=[], symbol='091990', price=1000.0, qty=1.0, timestamp=1234512340)
DEBUG monitor.messages               Created: MarketClosed(chains=[], total_ticks=2)
DEBUG monitor.facade                 Handler: market_closed for MarketClosed(chains=[], total_ticks=2)
```


## Support

Please [open an issue](https://github.com/yoonbae81/yquant/issues/new) for support.


## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/yoonbae/yquant/compare/).


## Testing

Test codes are prepared in _tests/_ based on [PyTest](https://docs.pytest.org/en/latest/) framework.
