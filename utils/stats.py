import time
from datetime import datetime
from typing import Dict, List

from bson import ObjectId
from cachetools import cached, TTLCache

from utils.modes import Modes
from utils.timer import RepeatedTimer
from utils.utils import log, ClearQuestion
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.foodle import Foodle


class Stats:
    def __init__(self, app: 'Foodle'):
        self.app = app
        self.__start_time_epoc = time.time()

        self.stats_db = self.app.db.stats_db
        self.total_stats_db = self.app.db.stats_db['count']
        self.count: Dict[int, List[str, int]] = {'total': 0, 'daily': {self.__today(): 0}}

        self.requests: Dict[int, List[Dict]] = {'total': 0, 'backlog': []}
        try:
            self.total_reqsObjID = str(self.total_stats_db.find_one()['_id'])
        except TypeError:
            self.total_stats_db.insert_one({})
            self.total_reqsObjID = str(self.total_stats_db.find_one()[
                                           '_id'])  # i know .__inserted_id, but it doesn't seem to work  # covers initial database creation
        self._load_request_count()
        self.rt_reqs = RepeatedTimer(60 * 5, self.__SendStatsData)  # run every 5 minutes

    def todo(self):
        wordsscema = {
            'pizza': [{'mode': Modes.DAILY, 'time': time.time()}, {'mode': Modes.INFINITE, 'time': time.time()}],
            'candy': [{'mode': Modes.DAILY, 'time': time.time()}], }
        pass

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
        req_count = self.total_stats_db.find_one({'_id': ObjectId(self.total_reqsObjID)})
        try:
            dailies = req_count['count']['dailies']
        except KeyError:
            dailies = {'2022-04-31': 4903, '2022-05-01': 200}
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
