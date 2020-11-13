import os
import json
import sqlalchemy

from cs50 import SQL
from flask import Flask, flash, render_template, request, jsonify, session, redirect
from flask_session import Session
from tempfile import mkdtemp
from flask_talisman import Talisman
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
# from werkzeug.exceptions import (default_exceptions, HTTPException,
#                                  InternalServerError)
# from werkzeug.security import check_password_hash, generate_password_hash

from xwind import (last_metar_raw, last_taf_raw, get_name, runways,
                   wind_direction, format_taf, wind_strength,
                   weather_times, weather_types, get_ident, headings,
                   runways_data, get_code, get_notams)

# Configure application
app = Flask(__name__)
app.config.from_object(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

SELF = "'self'"
talisman = Talisman(
    app,
    content_security_policy={
        'default-src': [
            SELF,
            'fonts.googleapis.com',
            'fonts.gstatic.com',
            'https://www.googletagmanager.com/',
            'www.google-analytics.com',
        ],
        'img-src': [
            '*',
            SELF,
            'www.w3.org',
            'data:',
            'https:;',
            'www.google-analytics.com',
            'https://www.googletagmanager.com/',
        ],
        'script-src': [
            SELF,
            'www.google-analytics.com',
            'https://www.googletagmanager.com/,
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

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

db = SQL('postgres://yslseapkhkqvfs:1296eb1622d1fc4fdc7864b5109102138cb7c3092199afdc7b747e5fd0b36bde@ec2-54-221-214-183.compute-1.amazonaws.com:5432/dau286g9ftm2ei')

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/index_app", methods=["GET", "POST"])
def index_app():
    station = request.args.get("form_data")
    ident = get_ident(station)
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
    notams_list = get_notams(ident)
    return jsonify(metar_text, taf_text, airport_name, ident, rwy_list, heading_list, wind_dir, wind_str, wx_times, wx_types, rwy_data, notams_list)

@app.route("/about", methods=["GET"])
def about():
    if request.method == 'GET':
        return render_template("about.html")

@app.route("/notams", methods=["GET", "POST"])
def notams():
    return render_template("notams.html")

@app.route("/notams_app", methods=["GET", "POST"])
def notams_app():
    station = request.args.get("form_data")
    print(station)
    ident = get_ident(station)
    notams_list = get_notams(ident)
    airport_name = get_name(ident)
    code = get_code(ident)
    #print(code)
    return jsonify(notams_list, airport_name, code)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
        # Checking for invalid fields or users already exist
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            flash('Please provide your username and password to register', "danger")
            return redirect('/register')
        else:
            if request.form.get("password") != request.form.get("confirmation"):
                flash('You did not enter your password correctly twice', "danger")
                return redirect('/register')

            username = request.form.get("username")

            try:
                if username == db.execute("SELECT username FROM users WHERE username = :username",
                                          username=username)[0]["username"]:
                    flash('Username already exists, please log in using your password', "warning")
                    return redirect("/register")
            except Exception:
                # Store the PW hash and username into database
                pw_hash = generate_password_hash(request.form.get("password"))
                db.execute("INSERT INTO users (username, hash, permission_level) VALUES (:username, :pw_hash, '0')",
                           username=username, pw_hash=pw_hash)
                
                # Consider the user as being logged in after being registered
                session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username",
                                                username=username)[0]["id"]
                flash('You have been successfully registered', 'danger')
                return redirect("/")

@app.route("/check", methods=["GET"])
def check():
    username = request.args.get("username")
    # Checking if there is an error while check for username, then check if at least 1 char has been entered
    # Return true if taken, false if not
    try:
        name_check = db.execute("SELECT username FROM users WHERE username = :username",
                                username=username)[0]["username"]
    except Exception:
        if len(username) >= 1:
            return jsonify(True)
    return jsonify(False)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('You must provide your username', "danger")
            return render_template("/login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('You must provide your password', "danger")
            return render_template("/login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash('Invalid username and/or password', "danger")
            return render_template("/login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash('You have been succesfully logged in!', "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function




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