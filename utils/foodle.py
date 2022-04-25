import logging
from os import environ
from os.path import exists

from dotenv import load_dotenv
from flask import Flask

from utils.database import Database
from utils.filters import FaviconFilter
from utils import utils


class Foodle(Flask):
    def __init__(self, import_name: str, *args, **kwargs):
        super().__init__(import_name, *args, **kwargs)

        if exists('.env'):  # local work
            load_dotenv()
        self.db = Database(environ.get('mongopass'))
        self.stats = utils.Stats(self)  # keep this under db load
        self.configs()

    def configs(self):
        logging.getLogger('werkzeug').addFilter(FaviconFilter())
        self.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

        self.config["DEBUG"] = True


