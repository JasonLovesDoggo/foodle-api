from json import load
from random import choice, randrange
from typing import List, Tuple

import requests

modes = ['daily', 'hourly', 'infinite']
stat_types = ['win', 'lose', 'concede']
requests_dict = {'POST': [],
                 'GET': ['/foodle/version', '/foodle/word/daily', '/foodle/word/hourly', '/foodle/word/infinite']}
VERSION = 'v1'
BASE = 'http://127.0.0.1:5000/'
URI_BASE = f'{BASE}/{VERSION}'
Errored = False
statuss: List[Tuple] = []

with open('../data/wordlist.json', 'r') as wlr:
    words = load(wlr)

def prGreen(prt):
    print("\033[92m {}\033[00m".format(prt))


def prRed(prt):
    print("\033[91m {}\033[00m".format(prt))


def send_stats_POST(stat: str):
    stat_uri_base = f'{URI_BASE}/foodle/stats/{stat}'
    for mode in modes:
        word = choice(words)
        uri = f'{stat_uri_base}/{mode}/{word}/{randrange(1, 6)}'
        statuss.append((uri, send_req_POST(uri)))

def test_all_words():
    for word in words:
        def_uri = URI_BASE + f'/foodle/definition/{word}'
        req = requests.get(def_uri)
        sc = req.status_code
        statuss.append((def_uri, sc))


def main():
    for stat in stat_types:
        send_stats_POST(stat)
    for uri in requests_dict['POST']:
        statuss.append((URI_BASE + uri, send_req_POST(URI_BASE + uri)))
    for uri in requests_dict['GET']:
        statuss.append((URI_BASE + uri, send_req_GET(URI_BASE + uri)))
    test_all_words()
    for uri, response in statuss:
        if response != 200:
            global Errored
            Errored = True
            prRed(f'{uri} failed with error {response}')
        prGreen(f'{uri} Successful!')

    if not Errored:  # no it can't ignore the IDE
        prGreen(f'\nAll tests Successful')


def send_req_POST(path):
    req = requests.post(path)
    return req.status_code


def send_req_GET(path):
    req = requests.get(path)
    return req.status_code


if __name__ == '__main__':
    main()
