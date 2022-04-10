from sys import stdout

from werkzeug.exceptions import HTTPException
from random import randrange

from flask import redirect, Flask, render_template

# from apiclient.discovery import build
# from oauth2client.service_account import ServiceAccountCredentials
# from flask_cors import CORS
from utils import *
import logging  # will only be using for exceptions

logging.basicConfig(
    format="%(asctime)s - [%(name)s | %(filename)s:%(lineno)d] - %(levelname)s - %(message)s",
    filename="api.log",
    filemode="w+",
    level=logging.INFO,
)
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(stdout))

app = Flask(__name__, template_folder='templates')
app.config["DEBUG"] = True


# CORS(app)

@app.route('/')
def index():
    return redirect('https://nasoj.me')


@app.errorhandler(HTTPException)
def function_name(error):
    num = randrange(1, 3)
    return render_template('error.html', content=f"https://http.{'cat' if num == 1 else 'dog'}/{error.code}.jpg",
                           error=error)


@app.get('/v1/foodle/definition/<word>')
def definition(word):
    return get_word(word)


@app.get('/v1/foodle/version')
def version():
    return jsonify(number)


@app.get("/v1/foodle/word/daily")
def search_query_daily():
    return CreateWordResponse(get_daily(), 200), 200


@app.get("/v1/foodle/word/hourly")
def search_query_hourly():
    hourly_word = 'hourly'  # Better Logic
    return CreateWordResponse(hourly_word, 200), 200


@app.get("/v1/foodle/word/infinite")
def search_query_infinite():
    infinite_word = 'infinite'  # Better Logic
    return CreateWordResponse(infinite_word, 200), 200


@app.route("/v1/foodle/stats/<mode>/<action>",
           methods=["POST"])  # i know app.post but a plugin im using to debug doesn't
def statistics(mode: str, action: str):
    if mode.lower == 'daily':
        if action.lower() == 'win':
            pass
    return f'{mode} x {action}'
