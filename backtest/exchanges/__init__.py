from typing import Protocol

from backtest.data import Msg


class Exchange(Protocol):
    """
    Exchange protocol for static duck typing. See [PEP 544](https://www.python.org/dev/peps/pep-0544/) for details,
    """

    def order(self,
              symbol: str,
              price: float,
              quantity: float) -> Msg:
        pass
