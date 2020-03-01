import multiprocessing
import time
from collections import namedtuple
import logging
from os import listdir
from os.path import exists, isfile, isdir, join, basename

from backtester import logger

Tick = namedtuple('Tick', 'symbol price quantity timestamp')


def _parse(line: str) -> Tick:
    symbol, price, quantity, timestamp = line.split()
    return Tick(symbol, float(price), float(quantity), int(timestamp))


def _list_dir(path: str):
    assert isdir(path)

    result = []
    for f in listdir(path):
        p = join(path, f)
        if isfile(p):
            result.append(p)

    return sorted(result)


def _get_tick(path: str) -> Tick:
    if not exists(path):
        raise FileNotFoundError(path)

    files = [path] if isfile(path) else _list_dir(path)

    for file in files:
        with open(file, 'rt') as f:
            for i, line in enumerate(f, 1):
                try:
                    yield _parse(line)
                except ValueError:
                    logger.error(f'{basename(file)} line {i} [{line.strip()}]')
                    # continue


def _get_router(queues):
    counter = {queue: 0 for queue in queues}
    assigned = {}

    def fn(symbol):
        try:
            queue = assigned[symbol]

        except KeyError:
            queue = min(counter, key=counter.get)
            assigned[symbol] = queue
            counter[queue] += 1

        return queue

    return fn


def run(config, tick_queues, log_queue):
    logger.config(log_queue)
    route = _get_router(tick_queues)

    count = 0
    for tick in _get_tick(config['ticks']):
        queue = route(tick.symbol)
        queue.put(tick)
        count += 1

    logger.info(f'Fetched {count} ticks')
    [queue.put(None) for queue in tick_queues]

    time.sleep(0.5)
    log_queue.put_nowait(None)
