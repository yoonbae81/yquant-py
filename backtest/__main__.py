import json
import logging
from collections import defaultdict
from multiprocessing import cpu_count
from pathlib import Path
from time import time
from typing import List, Any

import argparse

from .analyzer import Analyzer
from .broker import Broker
from .fetcher import Fetcher
from .ledger import Ledger
from .router import Router

logger = logging.getLogger(Path(__file__).stem)


def run(market: str,
        strategy: str,
        ticks_dir: str,
        ledger_dir: str,
        cash: float = 1_000_000):
    logger.info('Started')

    fetcher = Fetcher(Path(ticks_dir))
    analyzers = [Analyzer(strategy)
                 for _ in range((cpu_count() or 2) - 1)]
    broker = Broker(market, strategy, cash)
    ledger = Ledger(Path(ledger_dir))
    nodes: List[Any] = [ledger, broker, *analyzers, fetcher]

    router = Router()
    router.connect(nodes)

    nodes.insert(0, router)
    [node.start() for node in nodes]
    [node.join() for node in reversed(nodes)]


def validate(**config):
    required = {'market', 'strategy', 'ticks_dir', 'ledger_dir', 'cash'}

    if missing := required - set(config):
        print('Missing: ' + ', '.join(missing))
        return False

    dirs = {key: config[key] for key in config if key.endswith('_dir')}
    for k, v in dirs.items():
        if not Path(v).exists():
            print(f'{k}: {v} not found')
            return False

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json')
    args = parser.parse_args()

    with Path(args.config).open('rt', encoding='utf8') as f:
        config = json.load(f)

    if validate(**config):
        run(**config)
