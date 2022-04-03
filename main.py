from werkzeug.exceptions import HTTPException
from random import randrange

from flask import redirect, jsonify, json, Flask, render_template

# from apiclient.discovery import build
# from oauth2client.service_account import ServiceAccountCredentials
# from flask_cors import CORS
from utils import CreateWordResponse

app = Flask(__name__, template_folder='templates')
app.config["DEBUG"] = True
# CORS(app)

with open('json-data/version.json', 'r') as vj:
    number = json.load(vj)

with open('json-data/word_data.json', 'r') as wd:
    word_data = json.load(wd)


@app.route('/')
def index():
    return redirect('https://nasoj.me')

@app.errorhandler(HTTPException)
def function_name(error):
    num = randrange(1, 3)
    return render_template('error.html', content=f"https://http.{'cat' if num == 1 else 'dog'}/{error.code}.jpg", error=error)


@app.get('/v1/foodle/definition/<word>')
def definition(word):
    return jsonify(word_data[word])

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
