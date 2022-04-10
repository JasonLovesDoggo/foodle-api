import time
import sched
from os import environ
from urllib.parse import quote_plus as qp

import pymongo as pymongo
from dotenv import load_dotenv
from pymongo.server_api import ServerApi


class Database:
    def __init__(self, password):
        load_dotenv()
        self.client = pymongo.MongoClient(
            f"mongodb+srv://Jason:{qp(password)}@foodle.yiz9a.mongodb.net/{qp(environ.get('database'))}?retryWrites=true&w=majority",
            server_api=ServerApi('1'))
        self.WinBacklog: list[
            dict] = []  # clear this after it reac`````````````hes lets say 100 in length, so we don't overuse atlas
        self.LoseBacklog: list[dict] = []
        self.win_backlog = []
        self.sched = sched.scheduler(time.time, time.sleep)

    def win(self, mode, words):
        # have all the words be assigned a number to save db space
        data = {'time': int(time.time()), 'mode': mode, 'guesses': words}
        self.WinBacklog.append(data)

    def lose(self, mode, words, conceded: bool = False):
        # have all the words be assigned a number to save db space
        data = {'time': int(time.time()), 'mode': mode, 'guesses': words, 'conceded': conceded}
        self.LoseBacklog.append(data)

    def concede(self, mode, words):
        self.lose(mode, words, conceded=True)


db = Database(environ.get('mongopass'))
