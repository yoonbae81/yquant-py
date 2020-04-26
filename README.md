# Backtest
A backtest engine for developing algorithmic trading strategy.

[![PyPI](https://img.shields.io/pypi/v/backtest?color=%234ec726&style=flat-square)](https://pypi.org/project/backtest/)


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

The following usage is in `demo/main.py`. 

```python
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
```

## Support

Please [open an issue](https://github.com/yoonbae81/backtest/issues/new) for support.


## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/yoonbae/backtest/compare/).


## Testing

Test codes are located in _tests/_ based on [PyTest](https://docs.pytest.org/en/latest/) framework.

