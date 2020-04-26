import logging
from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Any

from .analyzer import Analyzer
from .broker import Broker
from .fetcher import Fetcher
from .ledger import Ledger
from .router import Router

logger = logging.getLogger(Path(__file__).name)


def run(market,
        strategy: str,
        ticks_dir: str,
        ledger_dir: str,
        initial_cash: float = 1_000_000):

    logger.debug('Started')

    fetcher = Fetcher(Path(ticks_dir))
    analyzers = [Analyzer(strategy)
                 for _ in range((cpu_count() or 2) - 1)]
    broker = Broker(market, strategy, initial_cash)
    ledger = Ledger(Path(ledger_dir))

    nodes: List[Any] = [ledger, broker, *analyzers, fetcher]
    router = Router(nodes)

    nodes.insert(0, router)
    [node.start() for node in nodes]
    [node.join() for node in reversed(nodes)]
