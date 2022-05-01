import json
import logging  # will only be using for exceptions
import time
from random import randrange
from sys import stdout

from flask import redirect, render_template, request, g, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string

from utils.foodle import Foodle
from utils.utils import RemoveUriArguments, get_word, get_daily, number

logging.basicConfig(format="%(asctime)s - [%(name)s | %(filename)s:%(lineno)d] - %(levelname)s - %(message)s",
                    filename="api.log", filemode="w+", level=logging.DEBUG)
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(stdout))

app = Foodle(__name__, template_folder='templates')


@app.route('/')
def index():
    app.stats.LogRequest(request.full_path, 0)
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
    app.stats.LogRequest(request.full_path, 100)
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
    app.stats.LogRequest(request.full_path, 101)
    return {'uptime': app.stats.uptime_info(),
            'requests': {'total': app.stats.total_requests(), 'today': app.stats.daily_requests()}}, 200


@app.get('/version')
def version():
    app.stats.LogRequest(request.full_path, 102)
    return jsonify(number)


@app.errorhandler(HTTPException)
def function_name(error):
    num = randrange(1, 3)  # 2/3 chance that it will show a random dog error 1/3 chance it will show a cat error
    return render_template('error.html', content=f"https://http.{'cat' if num == 1 else 'dog'}/{error.code}.jpg",
                           error=error)


@app.get('/v1/foodle/definition/<word>')  # if word not in dict try getting from the dictionaryapi
def definition(word):
    app.db.LogWord(word)
    app.stats.LogRequest(RemoveUriArguments(request, 'word'),
                         209)
    return get_word(word)


@app.get("/v1/foodle/word/daily")
def search_query_daily():
    app.stats.LogRequest(request.full_path, 210)
    return {'word': get_daily()}, 200


@app.get("/v1/foodle/word/hourly")
def search_query_hourly():
    app.stats.LogRequest(request.full_path, 211)
    hourly_word = 'hourly'  # Better Logic
    return {'word': hourly_word}, 200


@app.get("/v1/foodle/word/infinite")
def search_query_infinite():
    app.stats.LogRequest(request.full_path, 212)
    infinite_word = 'infinite'  # Better Logic
    return {'word': infinite_word}, 200


# I know app.post but a plugin im using to debug doesn't
@app.route("/v1/foodle/stats/win/<mode>/<word>/<guesses>", methods=["POST"])
def win(mode: str, word: str, guesses: int):
    app.stats.LogRequest(RemoveUriArguments(request, 'mode'), 200)
    app.db.win(mode, word, guesses)  # POST http://127.0.0.1:5000/v1/foodle/stats/win/daily/pizza/5
    return jsonify({'status': 200})


@app.route("/v1/foodle/stats/lose/<mode>/<word>/<guesses>", methods=["POST"])
def lose(mode: str, word: str, guesses: int):
    app.stats.LogRequest(RemoveUriArguments(request, 'mode'), 201)
    app.db.lose(mode, word, guesses)
    return jsonify({'status': 200})


@app.route("/v1/foodle/stats/concede/<mode>/<word>/<guesses>", methods=["POST"])
def concede(mode: str, word: str, guesses: int):
    app.stats.LogRequest(RemoveUriArguments(request, 'mode'), 202)
    app.db.concede(mode, word, guesses)
    return jsonify({'status': 200})
