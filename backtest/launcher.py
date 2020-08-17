import argparse
import json
import logging
import sys
from multiprocessing import cpu_count, Value
from pathlib import Path

from .analyzer import Analyzer
from .broker import Broker
from .fetcher import Fetcher
from .ledger import Ledger
from .router import Router
from .exchanges import Exchange

logger = logging.getLogger(Path(__file__).stem)

DEFAULTS = {
    'cash': 1_000_000,
    'ticks': 'ticks/',
    'ledger': 'ledger/',
    'symbols': 'symbols.json',
    'strategy': 'strategy',
}


def validate(**config):
    required = {'strategy', 'ticks', 'ledger', 'cash'}

    if missing := required - set(config):
        print('Missing key(s) in configuration: ' + ', '.join(missing))
        return False

    dirs = {key: config[key] for key in config if key.endswith('_dir')}
    for k, v in dirs.items():
        if not Path(v).exists():
            print(f'Not found dir: {v}')
            return False

    return True


def run(exchange: Exchange, strategy, initial_cash: float, ticks_dir: str, ledger_dir: str):
    # logger.info(f'Validating config: {config}')
    # if not validate(**config):
    #     sys.exit(1)

    logger.info('Starting')

    cash = Value('d', initial_cash)

    fetcher = Fetcher(Path(ticks_dir))
    analyzers = [Analyzer(cash, strategy)
                 for _ in range((cpu_count() or 2) - 1)]
    broker = Broker(cash, exchange)
    ledger = Ledger(Path(ledger_dir))

    nodes: list = [ledger, broker, *analyzers, fetcher]

    router = Router()
    [router.connect(node) for node in nodes]

    nodes.insert(0, router)
    [node.start() for node in nodes]
    [node.join() for node in reversed(nodes)]

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json')
    args = parser.parse_args(sys.argv[1:])

    with Path(args.config).open('rt', encoding='utf8') as f:
        config: dict = json.load(f)

    sys.exit(run(config))
