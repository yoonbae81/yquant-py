import argparse
import json
import sys

import requests

URLS = {
    'kospi': 'https://finance.daum.net/api/quotes/stocks?market=KOSPI',
    'kosdaq': 'https://finance.daum.net/api/quotes/stocks?market=KOSDAQ'
}

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'referer': 'https://finance.daum.net/domestic/all_quotes',
}


def _parse(res):
    data = json.loads(res.text)['data']
    for item in data:
        symbol = item.pop('code')[3:9]
        name = item.pop('name')
        yield symbol, name


def run(market):
    d = {}
    res = requests.get(URLS[market], headers=HEADERS)

    if res.status_code != 200:
        print('ERROR: HTTP Status Code {}'.format(res.status_code), file=sys.stderr)
        sys.exit(1)

    for symbol, name in _parse(res):
        d[symbol] = name

    return d


def save(data, file):
    json.dump(data,
              file,
              indent=4,
              sort_keys=True,
              ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('market')
    parser.add_argument('output', nargs='?', type=argparse.FileType('wt', encoding='utf-8'),
                        default=sys.stdout)
    args = parser.parse_args()

    data = run(args.market)
    save(data, args.output)

    if args.output is not sys.stdout:
        print(f'Saved in {args.output.name}')

""" Codelet for debug
res = requests.get(URLS['KOSPI'], headers=HEADERS)
res.status_code == 200
res.text
"""
