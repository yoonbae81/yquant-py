import logging
from time import sleep
from multiprocessing.connection import Connection
from os import listdir
from os.path import exists, isfile, isdir, join, basename
from threading import Thread

from .data import Tick, RESET, Msg

logger = logging.getLogger('fetcher')


class Fetcher(Thread):
    def __init__(self) -> None:
        super().__init__(name=self.__class__.__name__)

        self.output: Connection
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self) -> None:
        sleep(0.2)
        self.logger.debug('Running')

        for i in range(1, 10):
            msg = Msg('TICK', f's{i}')
            self.output.send(msg)
            print(f'Fetcher sent: {msg}')

            if i % 30 == 0:
                self.output.send(Msg('EOF'))

        sleep(0.2)
        self.output.send(Msg('EOD'))


def run(tick_dir, tick_queues, done):
    """Run fetcher

    Args:
        tick_dir (str): Directory that stores tick files.
        tick_queues (multiprocessing.Queue): Queue that connects *Analyzer* module.
        done (multiprocessing.Event): Will be set when there is no more tick.
    
    Returns:
        None
    """

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
