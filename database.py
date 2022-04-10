import time
from logging import getLogger
from os import environ
from urllib.parse import quote_plus as qp

import pymongo as pymongo
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

BACKLOGLIMIT = 25


class Database:
    def __init__(self, password):
        load_dotenv()
        self.client = pymongo.MongoClient(
            f"mongodb+srv://Jason:{qp(str(password))}@foodle.yiz9a.mongodb.net/{qp(str(environ.get('database')))}?retryWrites=true&w=majority",
            server_api=ServerApi('1'))
        self.stats_db = self.client.foodle_stats
        self.log = getLogger(__name__)
        # clear this after it's over the specified BACKLOGLIMIT, so we don't overuse atlas
        self.WinBacklog: list[dict] = []
        self.LoseBacklog: list[dict] = []

    def win(self, mode, words):
        # have all the words be assigned a number to save db space
        data = {'time': int(time.time()), 'mode': mode, 'guesses': words}
        self.WinBacklog.append(data)
        self.CheckBacklogs()

    def lose(self, mode, words, conceded: bool = False):
        # have all the words be assigned a number to save db space
        data = {'time': int(time.time()), 'mode': mode, 'guesses': words, 'conceded': conceded}
        self.LoseBacklog.append(data)
        self.CheckBacklogs()

    def concede(self, mode, words):
        self.lose(mode, words, conceded=True)

    def _SendWins(self):
        self.log.info(f'Sending {BACKLOGLIMIT} wins to the database')
        self.stats_db['wins'].insert_many(self.WinBacklog)
        self.WinBacklog = []

    def _SendLosses(self):
        self.log.info(f'Sending {BACKLOGLIMIT} losses to the database')
        self.stats_db['losses'].insert_many(self.LoseBacklog)
        self.LoseBacklog = []

    def CheckBacklogs(self):
        if len(self.WinBacklog) > BACKLOGLIMIT:
            self._SendWins()
        if len(self.LoseBacklog) > BACKLOGLIMIT:
            self._SendLosses()


db = Database(environ.get('mongopass'))
