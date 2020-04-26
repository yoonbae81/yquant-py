from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Any

from .analyzer import Analyzer
from .broker import Broker
from .fetcher import Fetcher
from .ledger import Ledger
from .router import Router


def run(market,
        strategy: str,
        ticks_dir: Path,
        ledger_dir: Path,
        initial_cash: float = 1_000_000):
    fetcher = Fetcher(ticks_dir)
    analyzers = [Analyzer(strategy)
                 for _ in range((cpu_count() or 2) - 1)]
    broker = Broker(market, strategy, initial_cash)
    ledger = Ledger(ledger_dir)

    nodes: List[Any] = [ledger, broker, *analyzers, fetcher]
    router = Router(nodes)

    nodes.insert(0, router)
    [node.start() for node in nodes]
    [node.join() for node in reversed(nodes)]
