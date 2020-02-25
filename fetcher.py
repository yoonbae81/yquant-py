from collections import namedtuple
from os import listdir
from os.path import exists, isfile, isdir, join

Tick = namedtuple('Tick', 'symbol price quantity timestamp')


def _parse(line):
    symbol, price, quantity, timestamp = line.split()
    return Tick(symbol, float(price), float(quantity), int(timestamp))


def _get_files(dir):
    assert isdir(dir)

    result = []
    for item in listdir(dir):
        path = join(dir, item)
        if isfile(path):
            result.append(path)

    return sorted(result)


def fetch(path):
    if not exists(path):
        raise FileNotFoundError(path)

    files = [path] if isfile(path) else _get_files(path)
    for file in files:
        with open(file, 'rt') as f:
            for i, line in enumerate(f):
                try:
                    yield _parse(line)
                except ValueError:
                    print(f"ERROR {file}:{i+1} [{line}]")
                    continue


if __name__ == '__main__':
    g = fetch('input')
    next(g)
    next(g)
    next(g)
    next(g)
    next(g)
    next(g)

