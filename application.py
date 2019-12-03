import os
import json
import sqlalchemy

from cs50 import SQL
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_session import Session
from tempfile import mkdtemp
from flask_talisman import Talisman
# from werkzeug.exceptions import (default_exceptions, HTTPException,
#                                  InternalServerError)
# from werkzeug.security import check_password_hash, generate_password_hash

from xwind import (last_metar_raw, last_taf_raw, get_name, runways,
                   wind_direction, format_taf, wind_strength,
                   weather_times, weather_types, get_ident, headings,
                   runways_data, get_code)

# Configure application
app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

SELF = "'self'"
talisman = Talisman(
    app,
    content_security_policy={
        'default-src': [
            SELF,
            'fonts.googleapis.com',
            'fonts.gstatic.com',
        ],
        'img-src': [
            '*',
            SELF,
            'www.w3.org',
            'data:',
            'https:;',
        ],
        'script-src': [
            SELF,
        ],
        'style-src': [
            SELF,
            'fonts.googleapis.com',
            'fonts.gstatic.com',

        ],
    },
    content_security_policy_nonce_in=['script-src'],
    feature_policy={
        'geolocation': '\'none\'',
    }
)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

'''
@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)'''


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
# db = SQL("sqlite:///database/xwind.db")
db = SQL('postgres://yslseapkhkqvfs:1296eb1622d1fc4fdc7864b5109102138cb7c3092199afdc7b747e5fd0b36bde@ec2-54-221-214-183.compute-1.amazonaws.com:5432/dau286g9ftm2ei')


@app.route("/", methods=["GET", "POST"])
###@talisman(
###    force_https='True'
###)
def index():

    if request.method == 'POST':

        ident = get_ident(request.form.get("station"))
        code = get_code(ident)
        metar_text = last_metar_raw(ident)
        taf_text = format_taf(last_taf_raw(ident))
        airport_name = get_name(ident)
        rwy_list = runways(code)
        heading_list = headings(code)
        wind_dir = wind_direction(ident)
        wind_str = wind_strength(ident)
        wx_times = weather_times(ident)
        wx_types = weather_types(ident)
        rwy_data = runways_data(code)
        return jsonify(metar_text, taf_text, airport_name, ident, rwy_list, heading_list, wind_dir, wind_str, wx_times, wx_types, rwy_data)
    else:
        return render_template("index.html")

@app.route("/about", methods=["GET"])
def about():
    if request.method == 'GET':
        return render_template("about.html")

''' def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler) '''


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)