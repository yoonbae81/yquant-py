import fetcher as sut


def test_parse():
    line = 'AAAAA 10000 10 1234512345'
    tick = sut._parse(line)

    assert tick.symbol == 'AAAAA'
    assert tick.price == 10000.0
    assert tick.quantity == 10.0
    assert tick.timestamp == 1234512345


def test_fetch():
    dir = 'input'
    sut.fetch(dir)
