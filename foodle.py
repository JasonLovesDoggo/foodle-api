import flask
from flask import jsonify, json

# from apiclient.discovery import build
# from oauth2client.service_account import ServiceAccountCredentials
# from flask_cors import CORS
from utils import CreateWordResponse

app = flask.Flask(__name__)
# CORS(app)

app.config["DEBUG"] = True
with open('version.json', 'r') as vj:
    number = json.load(vj)


@app.get('/v1/version')
def version():
    return jsonify(number)


@app.get("/v1/word/daily")
def search_query_daily():
    daily_word = 'daily'  # Better Logic
    return CreateWordResponse(daily_word, 200, 'daily')


@app.get("/v1/word/hourly")
def search_query_hourly():
    hourly_word = 'hourly'  # Better Logic
    return CreateWordResponse(hourly_word, 200, 'hourly')


@app.get("/v1/word/infinite")
def search_query_infinite():
    infinite_word = 'infinite'  # Better Logic
    return CreateWordResponse(infinite_word, 200, 'infinite')


@app.route("/v1/stats/<mode>/<action>", methods=["POST"])  # i know app.post but a plugin im using to debug doesn't
def statistics(mode: str, action: str):
    if mode.lower == 'daily':
        if action.lower() == 'win':
            pass
    return f'{mode} x {action}'


if __name__ == '__main__':
    app.run()
