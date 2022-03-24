from flask import redirect, jsonify, json, Flask

# from apiclient.discovery import build
# from oauth2client.service_account import ServiceAccountCredentials
# from flask_cors import CORS
from utils import CreateWordResponse

app = Flask(__name__)
app.config["DEBUG"] = True
# CORS(app)

with open('version.json', 'r') as vj:
    number = json.load(vj)


@app.route('/')
def index():
    return redirect('https://nasoj.me/404.html')

@app.errorhandler(status_code)
def function_name(error):
    num = random.randrange(1, 2)
    return render_template('templates/error.html', content=f"https://http.{'cat' if num == 1 else 'dog'}/{statut_code}.jpg", error_code=status_code),status_code

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return redirect('https://nasoj.me/404.html'), 404
    # CORS(app)


@app.get('/v1/foodle/version')
def version():
    return jsonify(number)


@app.get("/v1/foodle/word/daily")
def search_query_daily():
    daily_word = 'daily'  # Better Logic
    return CreateWordResponse(daily_word, 200, 'daily')


@app.get("/v1/foodle/word/hourly")
def search_query_hourly():
    hourly_word = 'hourly'  # Better Logic
    return CreateWordResponse(hourly_word, 200, 'hourly')


@app.get("/v1/foodle/word/infinite")
def search_query_infinite():
    infinite_word = 'infinite'  # Better Logic
    return CreateWordResponse(infinite_word, 200, 'infinite')


@app.route("/v1/foodle/stats/<mode>/<action>",
           methods=["POST"])  # i know app.post but a plugin im using to debug doesn't
def statistics(mode: str, action: str):
    if mode.lower == 'daily':
        if action.lower() == 'win':
            pass
    return f'{mode} x {action}'
