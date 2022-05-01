import time
from datetime import datetime
from typing import Dict

from cachetools import cached, TTLCache

from utils.utils import log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.foodle import Foodle

class Stats:
    def __init__(self, app: 'Foodle'):
        self.app = app
        self.__start_time_epoc = time.time()
        self.requests: Dict[str, Dict[str, int]] = {'total': 0, 'daily': {self.__today(): 0}}
        self._load_request_count()

    def log_request(self):
        # data = {'time': int(time.time()), 'mode': mode, 'word': word, 'guesses': str(guesses)}
        try:
            self.requests['daily'][self.__today()] += 1
            self.requests['total'] += 1
        except KeyError:
            self.requests['daily'][self.__today()] = 0  # fixes a KeyError on a new day
            self.log_request()

    @cached(cache=TTLCache(maxsize=1, ttl=60 * 5))  # 5 min TTL cache refresh time  with max size of 1
    def total_requests(self) -> int:
        # if not self.__total_requests_count:
        return int(self.requests['total'])

    @cached(cache=TTLCache(maxsize=1, ttl=60))  # 60s cache size with max size of 1
    def daily_requests(self) -> int:
        return int(self.requests['daily'][self.__today()])

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
        log.debug('requesting requests db')

        dailies_total = 0
        dailies = self.app.db.requests_db[self.__today()].find_one({})
        del dailies['_id']  # remove unnecessary id tag
        for unique_path in dailies.keys():
            dailies_total += dailies[unique_path]
        try:
            self.requests['daily'][self.__today()] += dailies_total
        except KeyError:
            self.requests['daily'][self.__today()] = 0
            self.requests['daily'][self.__today()] += dailies_total
        for collection in list(self.app.db.requests_db.list_collection_names()):  # ignore IDE
            collection_list = self.app.db.requests_db[collection].find({})
            for document in collection_list:
                del document['_id']  # remove the id from the document
                unique_requests = document.keys()
                for unique_request in unique_requests:
                    self.requests['total'] += (document[unique_request])

        log.info(f'successfully loaded {self.requests["total"]} requests')

    @staticmethod
    def __today() -> str:
        # always updated
        return str(datetime.today().strftime('%Y-%m-%d'))
