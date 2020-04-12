import logging
import time
from multiprocessing import Event
from os import listdir
from os.path import exists, isfile, isdir, join, basename

from .data import Tick

logger = logging.getLogger('fetcher')


def run(ticks_dir: str, tick_queues: [], done: Event):
    count = 0
    route = _get_router(tick_queues)
    for t in _get_tick(ticks_dir):
        queue = route(t.symbol)
        queue.put(t)
        count += 1

    logger.info(f'Fetched {count} ticks')
    time.sleep(2)
    done.set()


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
                    continue


def _list_dir(path: str) -> []:
    assert isdir(path)

    result = []
    for f in listdir(path):
        p = join(path, f)
        if isfile(p):
            result.append(p)

    return sorted(result)


def _parse(line: str) -> Tick:
    symbol, price, volume, timestamp = line.split()

    return Tick(
        symbol,
        float(price),
        float(volume),
        int(timestamp)
    )


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
