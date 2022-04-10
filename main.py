from os import environ
from sys import stdout

from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
from random import randrange

from flask import redirect, Flask, render_template, request

from database import Database
from utils import *
import logging  # will only be using for exceptions

logging.basicConfig(format="%(asctime)s - [%(name)s | %(filename)s:%(lineno)d] - %(levelname)s - %(message)s",
                    filename="api.log", filemode="w+", level=logging.INFO, )
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(stdout))

app = Flask(__name__, template_folder='templates')
app.config["DEBUG"] = True
load_dotenv()
db = Database(environ.get('mongopass'))

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
    db.LogRequest(request.full_path)  # TODO have a seperate db list with just word count guesses
    return get_word(word)


@app.get('/v1/foodle/version')
def version():
    db.LogRequest(request.full_path)
    return jsonify(number)


@app.get("/v1/foodle/word/daily")
def search_query_daily():
    db.LogRequest(request.full_path)
    return CreateWordResponse(get_daily(), 200), 200


@app.get("/v1/foodle/word/hourly")
def search_query_hourly():
    db.LogRequest(request.full_path)
    hourly_word = 'hourly'  # Better Logic
    return CreateWordResponse(hourly_word, 200), 200


@app.get("/v1/foodle/word/infinite")
def search_query_infinite():
    db.LogRequest(request.full_path)
    infinite_word = 'infinite'  # Better Logic
    return CreateWordResponse(infinite_word, 200), 200


# I know app.post but a plugin im using to debug doesn't
@app.route("/v1/foodle/stats/win/<mode>/<word>/<guesses>", methods=["POST"])
def win(mode: str, word: str, guesses: int):
    db.LogRequest(RemoveUriArguments(request, 'mode'))
    db.win(mode, word, guesses)  # POST http://127.0.0.1:5000/v1/foodle/stats/win/daily/pizza/5
    return jsonify({'status': 200})


@app.route("/v1/foodle/stats/lose/<mode>/<word>/<guesses>", methods=["POST"])
def lose(mode: str, word: str, guesses: int):
    db.LogRequest(RemoveUriArguments(request, 'mode'))
    db.lose(mode, word, guesses)
    return jsonify({'status': 200})


@app.route("/v1/foodle/stats/concede/<mode>/<word>/<guesses>", methods=["POST"])
def concede(mode: str, word: str, guesses: int):
    db.LogRequest(RemoveUriArguments(request, 'mode'))
    db.concede(mode, word, guesses)
    return jsonify({'status': 200})
