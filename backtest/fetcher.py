import logging
import time
from multiprocessing import Event
from os import listdir
from os.path import exists, isfile, isdir, join, basename

from .data import Tick, RESET

logger = logging.getLogger('fetcher')


def run(tick_dir: str, tick_queues: [], done: Event):
    files = [tick_dir] if isfile(tick_dir) else _list_dir(tick_dir)
    route = _get_router(tick_queues)

    count = 0
    for file in files:
        for t in _read_tick(file):
            queue = route(t.symbol)
            queue.put(t)
            count += 1

        logger.debug(f'Sending RESET messages (End of {file})')
        [queue.put(RESET) for queue in tick_queues]

    logger.info(f'Fetched {count} ticks')
    time.sleep(2)
    done.set()


def _read_tick(file):
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
