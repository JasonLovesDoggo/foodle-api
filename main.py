import flask
from flask import redirect

app = flask.Flask(__name__)
@app.route('/')
def index():
    return redirect('nasoj.me')

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return redirect('nasoj.me/404.html'), 404

