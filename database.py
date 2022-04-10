from datetime import datetime
import time
from logging import getLogger
from os import environ
from os.path import exists
from urllib.parse import quote as pq
import pymongo as pymongo
from bson import ObjectId
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

BACKLOGLIMIT = 25


class Database:
    def __init__(self, password):
        if exists('.env'):
            load_dotenv()
        self.client = pymongo.MongoClient(
            f"mongodb+srv://Jason:{pq(str(password))}@foodle.yiz9a.mongodb.net/{pq(str(environ.get('database')))}?retryWrites=true&w=majority",
            server_api=ServerApi('1'))
        self.stats_db = self.client.foodle_stats
        self.requests_db = self.client.requests_db
        self.RequestLogs = {}  # dont change
        self.log = getLogger(__name__)
        # clear this after it's over the specified BACKLOGLIMIT, so we don't overuse atlas
        self.WinBacklog: list[dict] = []
        self.LoseBacklog: list[dict] = []
        self.OldReqDataID = {}  # So the db doesn't have to re-query the database every time it wants to update the requests
        self.SendRequestIN = 0  # see self.CheckBacklogs
        self.SetOldReqDataID()
        self.RequestLogs = self.requests_db[datetime.today().strftime('%Y-%m-%d')].find_one(ObjectId(self.OldReqDataID))

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
        x = datetime.today().strftime('%Y-%m-%d')
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

    def SetOldReqDataID(self):
        rdbd = self.requests_db[datetime.today().strftime('%Y-%m-%d')]
        if self.OldReqDataID == {}:
            self.OldReqDataID = (rdbd.find_one()['_id'])

    def _SendRequestData(self):
        self.log.info(f'Sending {BACKLOGLIMIT} Requests\'s data to the database')
        rdbd = self.requests_db[datetime.today().strftime('%Y-%m-%d')]
        print(self.RequestLogs)
        rdbd.find_one_and_replace({"_id": ObjectId(self.OldReqDataID)}, self.RequestLogs)

    def CheckBacklogs(self):
        self.SendRequestIN += 1
        if len(self.WinBacklog) >= BACKLOGLIMIT:
            self._SendWins()
        if len(self.LoseBacklog) >= BACKLOGLIMIT:
            self._SendLosses()
        if int(self.SendRequestIN) >= BACKLOGLIMIT:
            self._SendRequestData()
