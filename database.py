import pymongo as pymongo
from os import environ
from urllib.parse import quote_plus as qp

from dotenv import load_dotenv
from pymongo.server_api import ServerApi

load_dotenv()
client = pymongo.MongoClient(
    f"mongodb+srv://Jason:{qp(environ.get('mongopass'))}@foodle.yiz9a.mongodb.net/{qp(environ.get('database'))}?retryWrites=true&w=majority",
    server_api=ServerApi('1'))
db = client.test
