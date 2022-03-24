from flask import jsonify


def CreateWordResponse(word: str, status_code: int, mode: str):
    return jsonify(
        {
            'Status': status_code,
            'mode': mode,
            'word': word,
        }
    )

