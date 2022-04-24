from os import environ
from os.path import exists
from sys import stdout

from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string
from random import randrange

from flask import redirect, Flask, render_template, request
from database import Database
from utils import *
import logging  # will only be using for exceptions

logging.basicConfig(format="%(asctime)s - [%(name)s | %(filename)s:%(lineno)d] - %(levelname)s - %(message)s",
                    filename="api.log", filemode="w+", level=logging.INFO)
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(stdout))

app = Flask(__name__, template_folder='templates')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.stats = Stats()

# app.config["DEBUG"] = True
if exists('.env'):
    load_dotenv()
db = Database(environ.get('mongopass'))


@app.route('/')
def index():
    return redirect('https://nasoj.me')


@app.route('/routes')
def routes():
    """Print all defined routes and their endpoint docstrings

    This also handles flask-router, which uses a centralized scheme
    to deal with routes, instead of defining them as a decorator
    on the target function.
    """
    api_routes = []
    for rule in app.url_map.iter_rules():
        try:
            if rule.endpoint != 'static':
                if hasattr(app.view_functions[rule.endpoint], 'import_name'):
                    import_name = app.view_functions[rule.endpoint].import_name
                    obj = import_string(import_name)
                    api_routes.append({rule.rule: "%s\n%s" % (",".join(list(rule.methods)), obj.__doc__)})
                else:
                    api_routes.append({rule.rule: app.view_functions[rule.endpoint].__doc__})
        except Exception as exc:
            api_routes.append({rule.rule:
                                   "(%s) INVALID ROUTE DEFINITION!!!" % rule.endpoint})
            route_info = "%s => %s" % (rule.rule, rule.endpoint)
            app.logger.error("Invalid route: %s" % route_info, exc_info=True)
            # func_list[rule.rule] = obj.__doc__

    return jsonify(api_routes), 200


@app.route('/stats')
@app.route('/statistics')
@app.route('/info')
def statistics():
    return {'uptime': app.stats.uptime_info()}, 200


@app.errorhandler(HTTPException)
def function_name(error):
    num = randrange(1, 3)  # 2/3 chance that it will show a random dog error 1/3 chance it will show a cat error
    return render_template('error.html', content=f"https://http.{'cat' if num == 1 else 'dog'}/{error.code}.jpg",
                           error=error)


@app.get('/v1/foodle/definition/<word>')  # if word not in dict try getting from the dictionaryapi
def definition(word):
    db.LogWord(word)
    db.LogRequest(RemoveUriArguments(request, 'word'))  # TODO have a seperate db list with just word count guesses
    return get_word(word)


@app.get('/v1/foodle/version')
def version():
    db.LogRequest(request.full_path)
    return jsonify(number)


@app.get("/v1/foodle/word/daily")
def search_query_daily():
    db.LogRequest(request.full_path)
    return {'word': get_daily()}, 200


@app.get("/v1/foodle/word/hourly")
def search_query_hourly():
    db.LogRequest(request.full_path)
    hourly_word = 'hourly'  # Better Logic
    return {'word': hourly_word}, 200


@app.get("/v1/foodle/word/infinite")
def search_query_infinite():
    db.LogRequest(request.full_path)
    infinite_word = 'infinite'  # Better Logic
    return {'word': infinite_word}, 200


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
