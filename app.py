import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from xwind import last_metar_raw, last_taf_raw, check_if_exist, check_local_code, search, get_name, login_required, wind_direction, format_taf

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
        station = request.form.get("station")

        try:
            ident = check_if_exist(station)
        except Exception:
            try:
                ident = check_local_code(station)
            except Exception:
                ident = search(station)

        metar_text = last_metar_raw(ident)
        taf_text = format_taf(last_taf_raw(ident))
        airport_name = get_name(ident)
        wind_dir = wind_direction(ident)
        print(wind_dir)
        return render_template("index.html", metar_text=metar_text, taf_text=taf_text, airport_name=airport_name, wind_dir=wind_dir)
    else:
        return render_template("index.html")


''' def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler) '''
