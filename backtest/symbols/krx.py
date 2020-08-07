import argparse
import json
import sys

import requests

URLS = {
    'kospi': 'https://finance.daum.net/api/quotes/stocks?market=KOSPI',
    'kosdaq': 'https://finance.daum.net/api/quotes/stocks?market=KOSDAQ'
}


def _parse(res):
    data = json.loads(res.text)['data']
    for item in data:
        symbol = item.pop('code')[3:9]
        name = item.pop('name')
        yield symbol, name


def _fetch(exchange):
    url = URLS[exchange]
    res = requests.get(url, headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        'referer': 'https://finance.daum.net/domestic/all_quotes',
    })

    if res.status_code != 200:
        print('ERROR: HTTP Status Code {}'.format(res.status_code), file=sys.stderr)
        sys.exit(1)

    d = {}
    for symbol, name in _parse(res):
        d[symbol] = {'exchange': exchange, 'name': name}

    return d


def run():
    data = {}
    for exchange in URLS:
        data |= _fetch(exchange)

    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output',
                        nargs='?',
                        type=argparse.FileType('wt', encoding='utf-8'),
                        default=sys.stdout)
    args = parser.parse_args()
    data = run()

    json.dump(data,
              args.output,
              indent=4,
              sort_keys=True,
              ensure_ascii=False)

    if args.output is not sys.stdout:
        print(f'Fetched {len(data):,} symbols')
        print(f'Saved in {args.output.name}')


if __name__ == '__main__':
    main()
