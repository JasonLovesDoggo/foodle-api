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
from typing import List, Dict, TYPE_CHECKING

from utils.timer import RepeatedTimer

BACKLOGLIMIT = 5  # change to 25 or 100 in prod

if TYPE_CHECKING:
    from utils.foodle import Foodle

class Database:
    def __init__(self, password, app: 'Foodle'):
        self.app = app
        if exists('../.env'):
            load_dotenv()  # mongo db client
        self.client = pymongo.MongoClient(
            f"mongodb+srv://Jason:{pq(str(password))}@foodle.yiz9a.mongodb.net/{pq(str(environ.get('database')))}?retryWrites=true&w=majority",
            server_api=ServerApi('1'))
        # the databases
        self.stats_db = self.client.foodle_stats
        self.requests_db = self.client.requests_db
        self.words_db = self.client.words_db
        # logger
        self.log = getLogger(__name__)

        # clear this after it's over the specified BACKLOGLIMIT, so we don't overuse atlas
        self.WinBacklog: List[Dict] = []
        self.LoseBacklog: List[Dict] = []
        self.WordObjID: str = ''
        self.RequestsObjID: str = ''
        # load the obj ids
        self.SetOldDataIDS()

        self.SendRequestIN = 0  # see self.CheckBacklogs
        self.RequestLogs = self.requests_db[datetime.today().strftime('%Y-%m-%d')].find_one(
            ObjectId(self.RequestsObjID))
        self.WordLogs = self.words_db[datetime.today().strftime('%Y-%m-%d')].find_one(ObjectId(self.WordObjID))
        self.rt_reqs = RepeatedTimer(60 * 5, self._SendRequestData)  # run every 5 minutes
        # uto-starts, no need of rt.start()
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
        self.app.stats.log_request()
        if path not in self.RequestLogs.keys():
            self.RequestLogs[path] = 0
        self.RequestLogs[path] += 1
        self.CheckBacklogs()

    def LogWord(self, word):
        if word not in self.WordLogs.keys():
            self.WordLogs[word] = 0
        self.WordLogs[
            word] += 1  # self.CheckBacklogs()   no need as its only called to the /definition/ path and that allready runs Log Request

    def _SendWins(self):
        self.log.info(f'Sending {BACKLOGLIMIT} wins to the database')
        self.stats_db['wins'].insert_many(self.WinBacklog)
        self.WinBacklog = []

    def _SendLosses(self):
        self.log.info(f'Sending {BACKLOGLIMIT} losses to the database')
        self.stats_db['losses'].insert_many(self.LoseBacklog)
        self.LoseBacklog = []

    def SetOldDataIDS(self):
        """ So the db doesn'ttttt have to re-query the database every time it wants to update the requests  """
        collist = self.requests_db.list_collection_names()  # both req and word db collection names should be the same
        today: str = datetime.today().strftime('%Y-%m-%d')
        rdbd = self.requests_db[today]
        wdb = self.words_db[today]
        if today not in collist:  # If it's a new day and a collection for that day's data doesn't exit       TODO: slight bug someplace here
            self.RequestsObjID = rdbd.insert_one({"/v1/foodle/version/?": 1}).inserted_id
            self.WordObjID = wdb.insert_one({"umami": 1}).inserted_id
        self.RequestsObjID = str(rdbd.find_one()['_id'])
        self.WordObjID = str(wdb.find_one()['_id'])

    def _SendRequestData(self):
        self.log.info(f'Sending {BACKLOGLIMIT} Requests\'s data to the database')
        rdbd = self.requests_db[datetime.today().strftime('%Y-%m-%d')]
        self.log.debug(self.RequestLogs) #usually isn't needed
        rdbd.insert_many(self.RequestLogs)

        #rdbd.find_one_and_replace({"_id": ObjectId(self.RequestsObjID)}, self.RequestLogs)

    def _SendWordData(self):
        self.log.info(f'Sending {BACKLOGLIMIT} Words\'s data to the database')
        rdbd = self.words_db[datetime.today().strftime('%Y-%m-%d')]
        rdbd.find_one_and_replace({"_id": ObjectId(self.WordObjID)}, self.WordLogs)

    def CheckBacklogs(self):
        self.SendRequestIN += 1
        if len(self.WinBacklog) >= BACKLOGLIMIT:
            self._SendWins()
            self.WinBacklog = []
        if len(self.LoseBacklog) >= BACKLOGLIMIT:
            self._SendLosses()
            self.LoseBacklog = []
        if int(self.SendRequestIN) >= BACKLOGLIMIT:
            self.SendRequestIN = 0
            self._SendRequestData()
            self._SendWordData()
