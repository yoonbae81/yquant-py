import argparse
import json
import sys

import requests

URLS = {
    'KOSPI': 'https://finance.daum.net/api/quotes/stocks?market=KOSPI',
    'KOSDAQ': 'https://finance.daum.net/api/quotes/stocks?market=KOSDAQ'
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


def run():
    d = {}
    for market, url in URLS.items():
        res = requests.get(url, headers=HEADERS)

        if res.status_code != 200:
            print('ERROR: HTTP Status Code {}'.format(res.status_code), file=sys.stderr)
            sys.exit(1)

        for symbol, name in _parse(res):
            d[symbol] = {'name': name,
                         'market': market}

    return d


def save(data, filepath):
    with open(filepath, 'wt', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default='symbol.json')
    args = parser.parse_args()

    data = run()
    print(data)

    save(data, args.output)
    print(f'Saved in {args.output}')

""" Codelet for debug
res = requests.get(URLS['KOSPI'], headers=HEADERS)
res.status_code == 200
res.text
"""
