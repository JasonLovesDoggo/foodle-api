import json
from datetime import datetime
from os import system, getcwd
import time
from functools import lru_cache
from logging import getLogger
from cachetools import TTLCache, cached
import flask
from flask import jsonify
from nodejs.bindings import node_run

from utils.foodle import Foodle

log = getLogger(__name__)
day = f'{int(time.strftime("%d"))}/{int(time.strftime("%m"))}/{time.strftime("%Y")}'


def load_data():
    global number, word_data, wordlist, gen_words
    with open('./data/version.json', 'r') as vj:
        number = json.load(vj)
        log.info(f'loaded version num {number}')

    with open('./data/word_data.json', 'r') as wd:
        word_data = json.load(wd)
        log.info('loaded word data')

    with open('./data/wordlist.json', 'r') as wl:
        wordlist = json.load(wl)
        log.info('loaded word list')

    with open('./data/generated_words.json', 'r') as gw:
        gen_words = json.load(gw)
        log.info('loaded Generated words')


def reinstate_data():
    load_data()


def regen_data():
    system('node get_words.js')
    stderr, stdout = node_run('get_words.js')
    reinstate_data()


@cached(cache=TTLCache(maxsize=15, ttl=60 * 5))  # 5 mins with max size of 15
def check_day():
    d = f'{int(time.strftime("%d"))}/{int(time.strftime("%m"))}/{time.strftime("%Y")}'
    if gen_words['lastupdated'] != d:
        log.info('words regenerated')
        regen_data()


load_data()
check_day()
number = number  # this is to shut up intelisense
gen_words = gen_words  # this is to shut up intelisense


def HourReplacment(hour: str):  # im sure there is a builtin for this, but I don't know it
    hourmap = {'0': '12 AM', '1': '1 AM', '2': '2 AM', '3': '3 AM', '4': '4 AM', '5': '5 AM', '6': '6 AM', '7': '7 AM',
               '8': '8 AM', '9': '9 AM', '10': '10 AM', '11': '11 AM', '12': '12 PM', '13': '1 PM', '14': '2 PM',
               '15': '3 PM', '16': '4 PM', '17': '5 PM', '18': '6 PM', '19': '7 PM', '20': '8 PM', '21': '9 PM',
               '22': '10 PM', '23': '11 PM'}
    return hourmap[str(hour)]


@lru_cache(maxsize=1)
def get_daily():
    check_day()
    return gen_words['daily']


@lru_cache(1)
def get_version():
    return number


@lru_cache(maxsize=512)
def get_word(word: str):
    if len(word) != 5:
        return CreateErrorResponse('word must be 5 characters long', 400)  # 400 means bad request
    if word in wordlist:
        return jsonify(word_data[word])
    return CreateErrorResponse('word not in wordlist', 404)


def CreateErrorResponse(error: str, status_code: int):
    log.warning(f'User Error code: {status_code} error {error}')
    return jsonify({'status': status_code, 'error': error, })


def RemoveUriArguments(request: flask.Request, argument):
    argument_data = str(request.view_args[argument])
    uri_base = str(request.full_path).split(argument_data)[0]
    return uri_base


class Stats:
    def __init__(self, app: Foodle):
        self.app = app
        self.__start_time_epoc = time.time()
        self.__total_requests_count = None
        self.__daily_requests_count = None

    @cached(cache=TTLCache(maxsize=1, ttl=60 * 5))  # 5 min TTL cache refresh time  with max size of 1
    def total_requests(self) -> int:
        #if not self.__total_requests_count:
        self._load_request_count() #todo: find a better way to regen than to call that
        return int(self.__total_requests_count)

    @cached(cache=TTLCache(maxsize=1, ttl=60))  # 60s cache size with max size of 1
    def daily_requests(self) -> int:
        #if not self.__daily_requests_count:
        return int(self.__daily_requests_count)

    @cached(cache=TTLCache(maxsize=1, ttl=10))  # 10s cache size with max size of 1
    def uptime_info(self):
        """
        returns total uptime of the api
        uses a 15s TTL cache so that it doesn't get strained if used very often


        :return: dict total seconds in multiple formats
        """
        now = time.time() - self.__start_time_epoc  # total time in seconds

        days, hours, minutes, seconds = int(now // 86400), int(now // 3600 % 24), int(now // 60 % 60), int(now % 60)
        uptime_readable = {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}

        return {'total_seconds': int(now), 'readable': uptime_readable}

    def _load_request_count(self):
        today = datetime.today().strftime('%Y-%m-%d')
        log.debug('requesting requests db')
        self.__total_requests_count = 0
        self.__daily_requests_count = 0
        dailies = self.app.db.requests_db[today].find_one({})
        del dailies['_id']
        for unique_path in dailies.keys():
            self.__daily_requests_count += dailies[unique_path]

        for collection in list(self.app.db.requests_db.list_collection_names()):  # ignore IDE
            collection_list = self.app.db.requests_db[collection].find({})
            for document in collection_list:
                del document['_id']  # remove the id from the document
                unique_requests = document.keys()
                for unique_request in unique_requests:
                    self.__total_requests_count += (document[unique_request])

        log.info(f'successfully loaded {self.__total_requests_count} requests')
