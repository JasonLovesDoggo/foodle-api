import time
from datetime import datetime
from typing import Dict, List

from bson import ObjectId
from cachetools import cached, TTLCache

from utils.modes import Modes, Guesses
from utils.timer import RepeatedTimer
from utils.utils import log, ClearQuestion
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.foodle import Foodle


class Stats:
    def __init__(self, app: 'Foodle'):
        self.app = app
        self.__start_time_epoc = time.time()

        self.games_db = self.app.db.games
        self.stats_db = self.app.db.stats
        self.words_db = self.app.db.words
        self.total_stats_db = self.app.db.stats['count']
        self.count: Dict[int, List[str, int]] = {'total': 0, 'daily': {self.__today(): 0}}

        self.requests: Dict[int, List[Dict]] = {'total': 0, 'backlog': []}
        self.game_backlog: List[Dict] = []
        self.word_backlog: Dict[List[Dict]] = {}

        try:
            self.total_reqsObjID = str(self.total_stats_db.find_one()['_id'])
        except TypeError:
            self.total_stats_db.insert_one({})
            self.total_reqsObjID = str(self.total_stats_db.find_one()[
                                           '_id'])  # I know .__inserted_id, but it doesn't seem to work  # covers initial database creation
        self._load_request_count()
        self.rt_reqs = RepeatedTimer(60 * 5, self.__SendStatsData)  # run every 5 minutes
        self.rt_game = RepeatedTimer(60 * 5, self.__SendGameData)  # run every 5 minutes
        self.rt_words = RepeatedTimer(60 * 5 / 10, self.__SendWordsData)  # run every 5 minutes

    def log_game(self, word: str, guesses: Guesses, mode: Modes) -> None:
        data = {'time': int(time.time()), 'word': word, 'guesses': guesses, 'mode': mode}
        self.game_backlog.append(data)

    def log_word(self, word: str, mode: Modes) -> None:
        data = {'time': int(time.time()), 'mode': mode}
        try:
            self.word_backlog[word].append(data)
        except KeyError:
            self.word_backlog[word] = []
            self.log_word(word, mode)

    def schemeas(self):
        wordsscema: dict[
            str, list[dict[str, Modes | float]] | list[dict[str, Modes | float] | dict[str, Modes | float]]] = {
            'pizza': [{'mode': Modes.DAILY, 'time': time.time()}, {'mode': Modes.INFINITE, 'time': time.time()}],
            'candy': [{'mode': Modes.DAILY, 'time': time.time()}], }
        games_schema: list[dict[str, Modes | int | str] | dict[str, Modes | int | str]] = [
            {'time': int(time.time()), 'word': 'pizza', 'guesses': 1, 'mode': Modes.DAILY},
            {'time': int(time.time()), 'word': 'lolly', 'guesses': 3, 'mode': Modes.HOURLY}]
        pass

    def __SendWordsData(self) -> None:
        if not self.word_backlog:
            return  # if there is nothing to send, don't send anything
        log.info(f'sending words data')
        print(self.word_backlog)
        for word, data in self.word_backlog.items():
            print(f'{word=}')
            print(f'{data=}')
            self.words_db[word].insert_many(data)
        self.word_backlog = {}

    def __SendGameData(self) -> None:
        if not self.game_backlog:
            return  # if there is nothing to send, don't send anything
        log.info(f'sending {len(self.game_backlog)} games\'s data')
        self.games_db.insert_many(self.game_backlog)
        self.game_backlog = []

    def __SendStatsData(self) -> None:
        if not self.requests['backlog']:
            return  # if there is nothing to send, don't send anything
        log.info(f'sending {len(self.count["daily"])} requests\'s data')
        data = {'total': self.count['total'], 'dailies': self.count['daily']}
        self.total_stats_db.find_one_and_update({'_id': ObjectId(self.total_reqsObjID)}, {"$set": {'count': data}},
                                                upsert=True)
        self.stats_db['requests'].insert_many(self.requests['backlog'])
        self.requests['backlog'] = []

    def LogRequest(self, path: str, path_code: int) -> None:
        data = {'time': int(time.time()), 'path': ClearQuestion(str(path)), 'path_code': int(path_code)}
        self.requests['backlog'].append(data)
        self.count['total'] += 1
        try:
            self.count['daily'][self.__today()] += 1
        except KeyError:
            self.count['daily'][self.__today()] = 1

    @cached(cache=TTLCache(maxsize=1, ttl=60 * 5))  # 5 min TTL cache refresh time  with max size of 1
    def total_requests(self) -> int:
        return int(self.count['total'])

    @cached(cache=TTLCache(maxsize=1, ttl=60))  # 60s cache size with max size of 1
    def daily_requests(self) -> int:
        return int(self.count['daily'][self.__today()])

    @cached(cache=TTLCache(maxsize=1, ttl=10))  # 10s cache size with max size of 1
    def uptime_info(self):
        """
        returns total uptime of the api
        uses a 15s TTL cache so that it doesn't get strained if used very often
        :return: a dict that has uptime info in multiple formats
        """

        now = time.time() - self.__start_time_epoc  # total time in seconds
        days, hours, minutes, seconds = int(now // 86400), int(now // 3600 % 24), int(now // 60 % 60), int(now % 60)
        uptime_readable = {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}

        return {'total_seconds': int(now), 'readable': uptime_readable}

    def _load_request_count(self):
        log.debug('requesting requests db')

        req_count = self.total_stats_db.find_one({'_id': ObjectId(self.total_reqsObjID)})
        try:
            dailies = req_count['count']['dailies']
        except KeyError:
            dailies = {'2022-04-31': 4903, '2022-05-01': 200}
            """
            blank data for the first time the database is created... 
            in order to the api to generate the data, it needs to already have some data"""
            print('send a request to the api, the database needs information.')

        for day in dailies.keys():
            if day == self.__today():
                self.count['daily'][day] += dailies[day]

        self.count['daily'] = dailies
        try:
            self.count['total'] = req_count['count']['total']
        except KeyError:  # initial database creation
            self.count['total'] = 69000

        log.info(f'successfully loaded {self.count["total"]} requests')

    @staticmethod
    def __today() -> str:
        """
        :return:  the current date in the format of YYYY-MM-DD
        """
        # return '2022-05-01'  # uncomment this to test the program with a fixed date
        return str(datetime.today().strftime('%Y-%m-%d'))
