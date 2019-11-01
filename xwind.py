import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import requests

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database/xwind.db")


# Check if station match with ICAO or IATA ident
def check_if_exist(station):
    station = station.upper()

    if len(station) == 4:
        icao = db.execute("SELECT ident FROM airports WHERE ident=:station", station=station)[0]["ident"]
    elif len(station) == 3:
        icao = db.execute("SELECT ident FROM airports WHERE iata_code =:station", station=station)[0]["ident"]

    return icao


# Check if station match with a local_code
def check_local_code(station):
    station = station.upper()
    icao = db.execute("SELECT ident FROM airports WHERE local_code=:station", station=station)[0]["ident"]

    return icao


# Lookup through list of aiport names if nothing else matched
def search(station):
    station = station.upper()
    n = len(station) + 1
    while True:
        try:
            icao = db.execute(f"SELECT ident FROM airports WHERE name LIKE '%{station[:n]}%'ORDER BY type DESC")[0]["ident"]
            break
        except Exception:
            n = n - 1
    return icao


# Retrieve the raw text of last available TAF
def last_metar_raw(ident):
    url_response = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=metars"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                       # use if only want latest
        "&hoursBeforeNow=2"                  # required even if latest
        f"&stationString={ident}")            # station ICAO code

    root = ET.fromstring(url_response.read())

    if not (root.findall('data/METAR')):
        raw_text = "No weather available"
    else:
        raw_text = ("METAR " + root.find('data/METAR/raw_text').text)

    return raw_text


# Retrieve the raw text of last available TAF
def last_taf_raw(ident):
    url_response = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=tafs"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecent=true"                      # use if only want latest
        "&hoursBeforeNow=12"                  # required even if latest
        f"&stationString={ident}")            # station ICAO code

    root = ET.fromstring(url_response.read())

    if not (root.find('data/TAF')):
        raw_text = " "
    else:
        raw_text = root.find('data/TAF/raw_text').text

    return raw_text


# Make TAF more readeable (like directly on ADDS)
def format_taf(raw_text):
    separate = raw_text.split()
    formatted = []
    for word in separate:
        if word[:2] == "FM":
            formatted.append("\n" + word + " ")
        elif word == ("TEMPO" or "BECMG" or "PROB30" or "PROB40"):
            formatted.append("\n" + word + " ")
        else:
            formatted.append(word + " ")

    new_text = ("".join(formatted))

    new_text_row = new_text.split('\n')
    return(new_text_row)


# Get name of  matching airport
def get_name(ident):
    name = db.execute("SELECT name FROM airports WHERE ident = :ident", ident=ident)[0]["name"]
    return name


# Decorate routes to require login
# http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Create a list of all existing winds in METAR and TAF
def wind_direction(ident):
    winddir = []
    url_response_metar = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=metars"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecentForEachStation=constraint"  # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")            # station ICAO code

    root_metar = ET.fromstring(url_response_metar.read())

    if not (root_metar.findall('data/METAR')):
        winddir.append(" ")
    else:
        winddir.append(root_metar.find('data/METAR/wind_dir_degrees').text)

    url_response_taf = urllib.request.urlopen(
        "https://www.aviationweather.gov/adds/dataserver_current/httpparam?"
        "datasource=tafs"                     # 'metars' or 'tafs'
        "&requestType=retrieve"                 # -- don't touch --
        "&format=xml"                           # -- don't touch --
        "&mostRecentForEachStation=constraint"  # use if only want latest
        "&hoursBeforeNow=1.25"                  # required even if latest
        f"&stationString={ident}")            # station ICAO code

    root_taf = ET.fromstring(url_response_taf.read())

    if not (root_taf.findall('data/TAF')):
        winddir.append(" ")
    else:
        for taf in root_taf.findall('data/TAF/forecast'):
            try:
                winddir.append(taf.find('wind_dir_degrees').text)
            except:
                continue

    return winddir


'''def lookup(symbol):
    """Look up quote for symbol."""
    # Contact API
    try:
        api_key = 'pk_9a4852b6b0404c58b4642145bf88b6c2'
        response = requests.get(
            f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None'''


''' def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code '''
