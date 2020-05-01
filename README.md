# Backtest

[![PyPI version](https://img.shields.io/pypi/v/backtest.svg)](https://pypi.org/project/backtest/)
[![Python version](https://img.shields.io/pypi/pyversions/backtest.svg)](https://pypi.org/project/backtest/)
[![Test](https://github.com/yoonbae81/backtest/workflows/test/badge.svg)](https://github.com/yoonbae81/backtest/actions?query=workflow%3Atest)
[![Build](https://github.com/yoonbae81/backtest/workflows/build/badge.svg)](https://github.com/yoonbae81/backtest/actions?query=workflow%3Abuild)
[![Coverage](https://codecov.io/gh/yoonbae81/backtest/graph/badge.svg)](http://codecov.io/gh/yoonbae81/backtest)
[![Docs](https://readthedocs.org/projects/backtest/badge/?version=latest)](https://backtest.readthedocs.io/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A backtest engine for developing algorithmic trading strategy.


## Table of Contents

- [Backtest](#backtest)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Support](#support)
  - [Contributing](#contributing)
  - [Testing](#testing)


## Installation
```
pip install backtest
```


## Usage

The following will execute the backtest after loading configuration file, `config.json` in same directory.
```python
backtest [--config config.json]
````

Sample content of `config.json`
```json
{
    "market": "korea",
    "strategy": "dummy",
    "ticks_dir": "ticks",
    "ledger_dir": "ledger",
    "cash": 1000000
}
```

## Support

Please [open an issue](https://github.com/yoonbae81/backtest/issues/new) for support.


## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/yoonbae/backtest/compare/).


## Testing

Test codes are located in _tests/_ based on [PyTest](https://docs.pytest.org/en/latest/) framework.

