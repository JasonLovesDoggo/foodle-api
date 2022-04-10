import time
from logging import getLogger
from os import environ
from urllib.parse import quote as pq
import pymongo as pymongo
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

BACKLOGLIMIT = 1


class Database:
    def __init__(self, password):
        load_dotenv()
        self.client = pymongo.MongoClient(
            f"mongodb+srv://Jason:{pq(str(password))}@foodle.yiz9a.mongodb.net/{pq(str(environ.get('database')))}?retryWrites=true&w=majority",
            server_api=ServerApi('1'))
        self.stats_db = self.client.foodle_stats
        self.RequestLogs = {}  # dont change
        self.RequestLogs['total'] = 0
        # self.TotalRequests: int = int(self.stats_db.totalRequests)
        self.log = getLogger(__name__)
        # clear this after it's over the specified BACKLOGLIMIT, so we don't overuse atlas
        self.WinBacklog: list[dict] = []
        self.LoseBacklog: list[dict] = []

    def win(self, mode: str, word: str, guesses: int):
        mode = mode.lower()
        # TODO: have all the words be assigned a number to save db space
        data = {'time': int(time.time()), 'mode': mode, 'word': word, 'guesses': str(guesses)}
        self.WinBacklog.append(data)
        self.CheckBacklogs()

    def lose(self, mode: str, word: str, guesses: int, conceded: bool = False):
        data = {'time': int(time.time()), 'mode': mode, 'word': word, 'guesses': str(guesses), 'conceded': conceded}
        self.LoseBacklog.append(data)
        self.CheckBacklogs()

    def concede(self, mode: str, word: str, guesses: int):
        self.lose(mode, word, guesses, conceded=True)

    def LogRequest(self, path):
        self.RequestLogs['total'] += 1
        if path not in self.RequestLogs.keys():
            self.RequestLogs[path] = 0
        self.RequestLogs[path] += 1

    def _SendWins(self):
        self.log.info(f'Sending {BACKLOGLIMIT} wins to the database')
        self.stats_db['wins'].insert_many(self.WinBacklog)
        self.WinBacklog = []

    def _SendLosses(self):
        self.log.info(f'Sending {BACKLOGLIMIT} losses to the database')
        self.stats_db['losses'].insert_many(self.LoseBacklog)
        self.LoseBacklog = []

    def _SendRequestData(self):
        self.log.info(f'Sending {BACKLOGLIMIT} Requests\'s data to the database')
        self.stats_db['requests'].insert_many(self.RequestLogs)

    def CheckBacklogs(self):
        if len(self.WinBacklog) > BACKLOGLIMIT:
            self._SendWins()
        if len(self.LoseBacklog) > BACKLOGLIMIT:
            self._SendLosses()
