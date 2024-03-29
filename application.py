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
                   runways_data, get_code, get_notams, metar_raw, taf_raw)

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
GTAGMANAGER = "'sha256-jCuI4MS0nKOR/cY36AHvokkmI75rsuotXwaxTIb+6WI='"
GTAGMANAGER2 = "'sha256-4CsM37pCrcAxFW4ege3IDUx4QzrVh/ldzA9ZDByNRVk='"
GTAGMANAGER3 = "'sha256-EwX6EbcqoJqFzIbppZekjClvKwP8U0E9IUxfsybqio8='"
GTAGMANAGER4 = "'sha256-R3UqpDkOGnMCgjXw5VM0z21i805qX+o1v9rgbh3bT9Y='"
GTAGMANAGER5 = "'sha256-B9g90kmK6XzS6C6YVf3mQz5sVeq9LfaG58xRtZsAxwE='"
GTAGMANAGER6 = "'sha256-m2Uf5+C6AFmeaoE3JkBsgRn24KJr061woOcBO3euBUo='"
GTAGMANAGER7 = "'sha256-+jYVjw0U5Xd2JcP9SuuFwcr6PJOO3kT8RwcsYYGx3As='"
talisman = Talisman(
    app,
    content_security_policy={
        'default-src': [
            SELF,
            'fonts.googleapis.com',
            'fonts.gstatic.com',
            'www.google-analytics.com',
            'www.googletagmanager.com',
            'www.gstatic.com',
            'www.tagmanager.google.com',
            'www.google.com'
        ],
        'img-src': [
            SELF,
            'www.w3.org',
            'data:',
            'https:;',
            'www.google-analytics.com',
            'www.googletagmanager.com',
            'www.gstatic.com',
            'www.tagmanager.google.com',
        ],
        'script-src': [
            SELF,
            'www.google-analytics.com',
            'www.googletagmanager.com',
            'https://www.googletagmanager.com'
            'www.tagmanager.google.com',
            GTAGMANAGER,
            GTAGMANAGER2,
            GTAGMANAGER3,
            GTAGMANAGER4,
            GTAGMANAGER5,
            GTAGMANAGER6,
            GTAGMANAGER7
        ],
        'style-src': [
            SELF,
            'fonts.googleapis.com',
            'fonts.gstatic.com',
            'www.google-analytics.com',
            'www.googletagmanager.com',
            'www.gstatic.com',
            'www.tagmanager.google.com',
        ],
    },
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


db = SQL('postgresql://ohbzghuvifbqji:98678bba7c0ad4692d193d6c97d03c372a1e1de1637bb0d4196e6dfa7e2a6b99@ec2-52-207-74-100.compute-1.amazonaws.com:5432/d5gb21to36p7kt')

# db = SQL("sqlite:///xwind.db")

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
    ident_list = []
    ident_list.append(ident)
    notams_list = get_notams(ident_list)
    return jsonify(metar_text, taf_text, airport_name, ident, rwy_list, heading_list, wind_dir, wind_str, wx_times, wx_types, rwy_data, notams_list)

@app.route("/about", methods=["GET"])
def about():
    if request.method == 'GET':
        return render_template("about.html")

@app.route("/notams", methods=["GET", "POST"])
def notams():
    return render_template("notams.html")

@app.route("/weather", methods=["GET", "POST"])
def weather():
    return render_template("weather.html")

@app.route("/notams_app", methods=["GET", "POST"])
def notams_app():
    stations_string = request.args.get("form_data")
    stations = stations_string.split()
    airport_names = []
    ident_list = []

    for station in stations:
        ident = get_ident(station)
        # Will be in original order
        ident_list.append(ident)
        airport_names.append(get_name(ident))
    notams_list = get_notams(ident_list)
    return jsonify(notams_list, airport_names, ident_list)

@app.route("/weather_app", methods=["GET", "POST"])
def weather_app():
    stations_string = request.args.get("form_data")
    stations = stations_string.split()
    airport_names = []
    ident_list = []

    for station in stations:
        ident = get_ident(station)
        # Will be in original order
        ident_list.append(ident)
        airport_names.append(get_name(ident))
    metar_list = metar_raw(ident_list)
    taf_list = taf_raw(ident_list)
    return jsonify(metar_list, taf_list, airport_names, ident_list)


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == 'GET':
#         return render_template("register.html")
#     if request.method == 'POST':
#         # Checking for invalid fields or users already exist
#         if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
#             flash('Please provide your username and password to register', "danger")
#             return redirect('/register')
#         else:
#             if request.form.get("password") != request.form.get("confirmation"):
#                 flash('You did not enter your password correctly twice', "danger")
#                 return redirect('/register')

#             username = request.form.get("username")

#             try:
#                 if username == db.execute("SELECT username FROM users WHERE username = :username",
#                                           username=username)[0]["username"]:
#                     flash('Username already exists, please log in using your password', "warning")
#                     return redirect("/register")
#             except Exception:
#                 # Store the PW hash and username into database
#                 pw_hash = generate_password_hash(request.form.get("password"))
#                 db.execute("INSERT INTO users (username, hash, permission_level) VALUES (:username, :pw_hash, '0')",
#                            username=username, pw_hash=pw_hash)

#                 # Consider the user as being logged in after being registered
#                 session["user_id"] = db.execute("SELECT id FROM users WHERE username = :username",
#                                                 username=username)[0]["id"]
#                 flash('You have been successfully registered', 'danger')
#                 return redirect("/")

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
