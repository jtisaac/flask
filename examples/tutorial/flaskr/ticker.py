from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import requests
import json

bp = Blueprint("ticker", __name__)


@bp.route("/ticker", methods=('POST','GET'))
def index():
    """Create a new post for the current user."""
    json_response = ""
    if request.method == "POST":
        ticker_key = request.form["ticker_key"]
        error = None

        if not ticker_key:
            error = "Ticker is required."

        if error is not None:
            flash(error)
        else:
            # get the ticker info
            #response = requests.get('https://sandbox.tradier.com/v1/markets/options/lookup',
            #    params={'underlying': ticker_key},
            #    headers={'Authorization': 'Bearer sNhzFaRt7B2uRiX73um6JPDceWbm', 'Accept': 'application/json'}
            #)
            #json_response = response.json()


            response = requests.get('https://sandbox.tradier.com/v1/markets/timesales',
                params={'symbol': ticker_key, 'interval': '1min', 'start': '2021-02-01 09:30', 'end': '2021-02-05 16:00', 'session_filter': 'all'},
                headers={'Authorization': 'Bearer sNhzFaRt7B2uRiX73um6JPDceWbm', 'Accept': 'application/json'}
            )
            json_response = response.json()
            print(response.status_code)

            print(json_response)

            #return redirect(url_for("blog.index"))

    return render_template("ticker/ticker.html", ticker_info=json_response) #ticker_info=json.dumps(json_response)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")