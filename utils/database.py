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
        self.stats_db = self.client.stats
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
        self.WordLogs = self.words_db[datetime.today().strftime('%Y-%m-%d')].find_one(ObjectId(self.WordObjID))

    def win(self, mode: str, word: str, guesses: int):
        mode = mode.lower()
        data = {'time': int(time.time()), 'mode': mode, 'word': word, 'guesses': str(guesses)}
        self.WinBacklog.append(data)
        self.CheckBacklogs()

    def lose(self, mode: str, word: str, guesses: int, conceded: bool = False):
        data = {'time': int(time.time()), 'mode': mode, 'word': word, 'guesses': str(guesses), 'conceded': conceded}
        self.LoseBacklog.append(data)
        self.CheckBacklogs()

    def concede(self, mode: str, word: str, guesses: int):
        self.lose(mode, word, guesses, conceded=True)

    def LogRequest(self, path: str, request_path_code: int = 200) -> None:
        self.app.stats.LogRequest(path, request_path_code)

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
        today: str = datetime.today().strftime('%Y-%m-%d')
        wdb = self.words_db[today]
        self.WordObjID = str(wdb.find_one()['_id'])

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
            # self._SendRequestData()
            self._SendWordData()
