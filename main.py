import flask
from flask import redirect

app = flask.Flask(__name__)
@app.route('/')
def index():
    return redirect('nasoj.me')

