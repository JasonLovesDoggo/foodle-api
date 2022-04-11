from random import choice, randrange

import requests

modes = ['daily', 'hourly', 'infinite']
stat_types = ['win', 'lose', 'concede']
test_words = ["fresh", "crust", "serve", "flesh", "seedy", "corny"]
requests_dict = {'POST': [''], 'GET': ['/v1/foodle/version']}
VERSION = 'v1'
BASE = 'http://127.0.0.1:5000/'
URI_BASE = f'{BASE}/{VERSION}'
Errored = False
statuss: list[tuple] = []


def prGreen(prt):
    print("\033[92m {}\033[00m".format(prt))


def prRed(prt):
    print("\033[91m {}\033[00m".format(prt))


def send_stats_POST(stat: str):
    stat_uri_base = f'{URI_BASE}/foodle/stats/{stat}'
    for mode in modes:
        word = choice(test_words)
        uri = f'{stat_uri_base}/{mode}/{word}/{randrange(1, 6)}'
        statuss.append((uri, send_req_POST(uri)))


def main():
    for stat in stat_types:
        send_stats_POST(stat)
    for uri in requests_dict['POST']:
        statuss.append((uri, send_req_POST(URI_BASE + uri)))
    for uri in requests_dict['GET']:
        statuss.append((uri, send_req_GET(URI_BASE + uri)))
    for uri, response in statuss:
        if response != 200:
            global Errored
            Errored = True
            prRed(f'{uri} failed with error {response}')

    if not Errored:  # no it can't ignore the IDE
        prGreen(f'All tests Successful')


def send_req_POST(path):
    req = requests.post(path)
    return req.status_code


def send_req_GET(path):
    req = requests.get(path)
    return req.status_code


if __name__ == '__main__':
    main()
