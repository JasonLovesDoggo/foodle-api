from os import environ
from os.path import exists
from sys import stdout

from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string
from random import randrange

from flask import redirect, Flask, render_template, request, g
from utils.database import Database
from utils.filters import FaviconFilter
from utils.utils import *
import logging  # will only be using for exceptions

logging.basicConfig(format="%(asctime)s - [%(name)s | %(filename)s:%(lineno)d] - %(levelname)s - %(message)s",
                    filename="api.log", filemode="w+", level=logging.DEBUG)
log = logging.getLogger(__name__)

log.addHandler(logging.StreamHandler(stdout))
# logging filters
logging.getLogger('werkzeug').addFilter(FaviconFilter())
###


app = Flask(__name__, template_folder='templates')  # todo: subclass Flask with  custom stuff like db and stats
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

if exists('.env'):  # local work
    load_dotenv()
app.db = Database(environ.get('mongopass'))

app.stats = Stats(app)  # keep this under db load

app.config["DEBUG"] = True


@app.route('/')
def index():
    app.db.LogRequest(request.full_path)
    return redirect('https://nasoj.me/foodle/')


@app.before_request
def before():
    g.timeTaken = time.time()


@app.after_request
def after(response):
    data = response.get_json()
    if type(data) is dict:
        totaltime = str(f'{round(time.time() - g.timeTaken, 2)}s')
        data['timeTaken'] = totaltime

        response.data = json.dumps(data)

    return response


@app.route('/routes')
def routes():
    """Print all defined routes and their endpoint docstrings

    This also handles flask-router, which uses a centralized scheme
    to deal with routes, instead of defining them as a decorator
    on the target function.
    """
    app.db.LogRequest(request.full_path)
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
            api_routes.append({rule.rule: "(%s) INVALID ROUTE DEFINITION!!!" % rule.endpoint})
            route_info = "%s => %s" % (rule.rule, rule.endpoint)
            app.logger.error("Invalid route: %s" % route_info, exc_info=True)  # func_list[rule.rule] = obj.__doc__

    return jsonify(api_routes), 200


@app.route('/stats')
@app.route('/statistics')
@app.route('/info')
def statistics():
    app.db.LogRequest(request.full_path)
    return {'uptime': app.stats.uptime_info(),
            'requests': {'total': app.stats.total_requests(), 'today': app.stats.daily_requests()}}, 200


@app.errorhandler(HTTPException)
def function_name(error):
    num = randrange(1, 3)  # 2/3 chance that it will show a random dog error 1/3 chance it will show a cat error
    return render_template('error.html', content=f"https://http.{'cat' if num == 1 else 'dog'}/{error.code}.jpg",
                           error=error)


@app.get('/v1/foodle/definition/<word>')  # if word not in dict try getting from the dictionaryapi
def definition(word):
    app.db.LogWord(word)
    app.db.LogRequest(RemoveUriArguments(request, 'word'))  # TODO have a seperate db list with just word count guesses
    return get_word(word)


@app.get('/v1/foodle/version')
def version():
    app.db.LogRequest(request.full_path)
    return jsonify(number)


@app.get("/v1/foodle/word/daily")
def search_query_daily():
    app.db.LogRequest(request.full_path)
    return {'word': get_daily()}, 200


@app.get("/v1/foodle/word/hourly")
def search_query_hourly():
    app.db.LogRequest(request.full_path)
    hourly_word = 'hourly'  # Better Logic
    return {'word': hourly_word}, 200


@app.get("/v1/foodle/word/infinite")
def search_query_infinite():
    app.db.LogRequest(request.full_path)
    infinite_word = 'infinite'  # Better Logic
    return {'word': infinite_word}, 200


# I know app.post but a plugin im using to debug doesn't
@app.route("/v1/foodle/stats/win/<mode>/<word>/<guesses>", methods=["POST"])
def win(mode: str, word: str, guesses: int):
    app.db.LogRequest(RemoveUriArguments(request, 'mode'))
    app.db.win(mode, word, guesses)  # POST http://127.0.0.1:5000/v1/foodle/stats/win/daily/pizza/5
    return jsonify({'status': 200})


@app.route("/v1/foodle/stats/lose/<mode>/<word>/<guesses>", methods=["POST"])
def lose(mode: str, word: str, guesses: int):
    app.db.LogRequest(RemoveUriArguments(request, 'mode'))
    app.db.lose(mode, word, guesses)
    return jsonify({'status': 200})


@app.route("/v1/foodle/stats/concede/<mode>/<word>/<guesses>", methods=["POST"])
def concede(mode: str, word: str, guesses: int):
    app.db.LogRequest(RemoveUriArguments(request, 'mode'))
    app.db.concede(mode, word, guesses)
    return jsonify({'status': 200})
