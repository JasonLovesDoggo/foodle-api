import json
from functools import lru_cache
from logging import getLogger

import flask
from flask import jsonify

log = getLogger(__name__)

with open('data/version.json', 'r') as vj:
    number = json.load(vj)
    log.info(f'loaded version num {number}')

with open('data/word_data.json', 'r') as wd:
    word_data = json.load(wd)
    log.info('loaded word data')

with open('data/wordlist.json', 'r') as wl:
    wordlist = json.load(wl)
    log.info('loaded word list')

with open('data/generated_words.json', 'r') as gw:
    gen_words = json.load(gw)
    log.info('loaded Generated words')

def HourReplacment(hour: str):  # im sure there is a builtin for this, but I don't know it
    hourmap = {'0': '12 AM',
               '1': '1 AM',
               '2': '2 AM',
               '3': '3 AM',
               '4': '4 AM',
               '5': '5 AM',
               '6': '6 AM',
               '7': '7 AM',
               '8': '8 AM',
               '9': '9 AM',
               '10': '10 AM',
               '11': '11 AM',
               '12': '12 PM',
               '13': '1 PM',
               '14': '2 PM',
               '15': '3 PM',
               '16': '4 PM',
               '17': '5 PM',
               '18': '6 PM',
               '19': '7 PM',
               '20': '8 PM',
               '21': '9 PM',
               '22': '10 PM',
               '23': '11 PM'}
    return hourmap[str(hour)]

@lru_cache(maxsize=1)
def get_daily():
    return gen_words['daily']


@lru_cache
def get_version():
    return number


@lru_cache(maxsize=512)
def get_word(word: str):
    if len(word) != 5:
        return CreateErrorResponse('word must be 5 characters long', 400)  # 400 means bad request
    if word in wordlist:
        return jsonify(word_data[word])
    return CreateErrorResponse('word not in wordlist', 404)


def CreateErrorResponse(error: str, status_code: int):
    log.warning(f'User Error code: {status_code} error {error}')
    return jsonify({'status': status_code, 'error': error, })

def RemoveUriArguments(request: flask.Request, argument):
    argument_data = str(request.view_args[argument])
    uri_base = str(request.full_path).split(argument_data)[0]
    return uri_base

