# import os
import json

from cs50 import SQL
from flask import Flask, render_template, request, jsonify
from flask_session import Session
from tempfile import mkdtemp
# from werkzeug.exceptions import (default_exceptions, HTTPException,
#                                  InternalServerError)
# from werkzeug.security import check_password_hash, generate_password_hash

from xwind import (last_metar_raw, last_taf_raw, get_name, runways,
                   wind_direction, format_taf, wind_strength,
                   weather_times, weather_types, get_ident)

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database/xwind.db")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        ident = get_ident(request.form.get("station"))

        metar_text = last_metar_raw(ident)
        taf_text = format_taf(last_taf_raw(ident))
        airport_name = get_name(ident)

        return jsonify(metar_text, taf_text, airport_name, ident)
    else:
        return render_template("index.html")


# Check DB for runway list
@app.route("/get_rwy_list", methods=["POST"])
def rwy_list():
    ident = get_ident(request.args.get("station"))
    rwy_list = runways(ident)
    return jsonify(rwy_list)


# Ajax functions to return wind directions
@app.route("/get_wind_dir", methods=["POST"])
def get_wind_dir():
    ident = get_ident(request.args.get("station"))
    wind_dir = wind_direction(ident)
    return jsonify(wind_dir)


# Ajax functions to return wind strength
@app.route("/get_wind_str", methods=["POST"])
def get_wind_str():
    ident = get_ident(request.args.get("station"))
    wind_str = wind_strength(ident)
    return jsonify(wind_str)


# Ajax functions to return weather wind time
@app.route("/get_wx_times", methods=["POST"])
def get_wx_times():
    ident = get_ident(request.args.get("station"))
    wx_times = weather_times(ident)
    return jsonify(wx_times)


# Ajax functions to return weather wind time
@app.route("/get_wx_types", methods=["POST"])
def get_wx_types():
    ident = get_ident(request.args.get("station"))
    wx_types = weather_types(ident)
    return jsonify(wx_types)


''' def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler) '''
