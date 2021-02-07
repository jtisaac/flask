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

ticker_key_prior = None

bp = Blueprint("ticker", __name__)

@bp.route("/ticker", methods=('POST','GET'))
def index():
    # TODO: Show historical daily stock prices since the first stock (modify api call to https://documentation.tradier.com/brokerage-api/markets/get-history)
    # TODO: Allow multiple tickers to be entered
    # TODO: Add parameters (date range)
    """Return market data for ticker entered by user."""
    json_response = ""
    json_response_options = ""
    options_response = ""
    global ticker_key_prior

    if request.method == "POST":
        ticker_key = request.form.get("ticker_key", ticker_key_prior)
        option_date = request.form.get("option_date", None)

        error = None

        if not ticker_key:
            ticker_key = ticker_key_prior
            if not ticker_key:
                error = "Ticker is required."

        if error is not None:
            flash(error)
        
        else:
            if option_date is None:
                response = requests.get('https://sandbox.tradier.com/v1/markets/timesales',
                    params={'symbol': ticker_key, 'interval': '1min', 'start': '2021-02-01 09:30', 'end': '2021-02-05 16:00', 'session_filter': 'all'},
                    headers={'Authorization': 'Bearer sNhzFaRt7B2uRiX73um6JPDceWbm', 'Accept': 'application/json'}
                )
                json_response = response.json()
                ticker_key_prior = ticker_key
                print(response.status_code)

                print(json_response)
            else:
                response = requests.get('https://sandbox.tradier.com/v1/markets/timesales',
                    params={'symbol': ticker_key, 'interval': '1min', 'start': '2021-02-01 09:30', 'end': '2021-02-05 16:00', 'session_filter': 'all'},
                    headers={'Authorization': 'Bearer sNhzFaRt7B2uRiX73um6JPDceWbm', 'Accept': 'application/json'}
                )
                json_response = response.json()
                print(response.status_code)

                print(json_response)
                ticker_key_prior = ticker_key

                response = requests.get('https://sandbox.tradier.com/v1/markets/options/chains',
                    params={'symbol': ticker_key, 'expiration': option_date, 'greeks': 'true'},
                    headers={'Authorization': 'Bearer sNhzFaRt7B2uRiX73um6JPDceWbm', 'Accept': 'application/json'}
                )
                json_response_options = response.json()
                options_response = {
                    'call': [],
                    'put': []
                }
                for option in json_response_options["options"]["option"]:
                    options_response[option['option_type']].append({"strike": option['strike'], "price": (option['bid'] + option['ask']) / 2})

                print(response.status_code)
                print(json_response_options)

    return render_template("ticker/ticker.html", ticker_info=json_response, options_info=options_response) #ticker_info=json.dumps(json_response)