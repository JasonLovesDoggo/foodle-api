import json
from functools import lru_cache
from logging import getLogger

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


def CreateWordResponse(word: str, status_code: int, mode: str):
    return jsonify(
        {
            'Status': status_code,
            'mode': mode,
            'word': word,
        }
    )


def CreateErrorResponse(error: str, status_code: int):
    log.warning(f'User Error code: {status_code} error {error}')
    return jsonify(
        {
            'Status': status_code,
            'error': error,
        }
    )
